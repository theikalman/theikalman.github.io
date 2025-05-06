---
layout: post
title:  "Debugging PHP App in NeoVim with Launch Configuration"
date:   2025-05-06 06:00:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
---

Sometimes I need to debug PHP code in two different situations: a CLI (command-line) app and a web server app. While the way to run each one is slightly different, the steps are subtle, and I often forget the correct order for each case.
### NeoVim Plugin
- `mfussenegger/nvim-dap`
- `kristijanhusak/vim-dadbod-ui`
### Project Directory Structure
Assuming we have this project directory structure:
```
src
└── App.php -- This is the entry point for CLI app
index.php   -- This is the entry point for Server app
composer.json
flake.nix   -- Nix flake file (NixOS)
.user.ini   -- PHP ini configuration
.vscode
└── launch.json -- Launch configuration
```

I am currently using Nix package manager to setup environment for each project that I have. With nix it is much more convenient to setup PHP environment since I can enable and include necessary PHP extension that I need to have, in this case I need to have xdebug extension.

`flake.nix`:
```nix
{
  description = "debugphp";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nix-shell.url = "github:loophp/nix-shell";
    systems.url = "github:nix-systems/default";
  };

  outputs =
    inputs@{
      self,
      flake-parts,
      systems,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import systems;

      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          lib,
          ...
        }:
        let
          php = pkgs.api.buildPhpFromComposer {
            src = inputs.self;
            php = pkgs.php83; # Change to php56, php70, ..., php81, php82, php83 etc.
          };
        in
        {
          _module.args.pkgs = import self.inputs.nixpkgs {
            inherit system;
            overlays = [ inputs.nix-shell.overlays.default ];
            config.allowUnfree = true;
          };

          devShells.default = pkgs.mkShellNoCC {
            name = "php-devshell";
            buildInputs = [
              php
              php.packages.composer
              pkgs.phpunit
            ];
          };

          apps = {
            # nix run .#composer -- --version
            composer = {
              type = "app";
              program = lib.getExe (
                pkgs.writeShellApplication {
                  name = "composer";

                  runtimeInputs = [
                    php
                    php.packages.composer
                  ];

                  text = ''
                    ${lib.getExe php.packages.composer} "$@"
                  '';
                }
              );
            };

            # nix run .#phpunit -- --version
            phpunit = {
              type = "app";
              program = lib.getExe (
                pkgs.writeShellApplication {
                  name = "phpunit";

                  runtimeInputs = [ php ];

                  text = ''
                    ${lib.getExe pkgs.phpunit} "$@"
                  '';
                }
              );
            };
          };
        };
    };
}
```

`composer.json`:
```json
{
    "name": "ajiyakin/debugphp",
    "description": "Sample project to demonstrate how to debug PHP in NeoVim",
    "type": "project",
    "require": {
        "guzzlehttp/guzzle": "^7.9"
    },
    "require-dev": {
        "phpunit/phpunit": "^8.5",
        "ext-xdebug": "*",
        "phpunit/php-code-coverage": "^7.0"
    },
    "license": "MIT",
    "autoload": {
        "psr-4": {
            "Ajiyakin\\Debugphp\\": "src/"
        }
    },
    "authors": [
        {
            "name": "AjiYakin",
            "email": "ajiyakin91@gmail.com"
        }
    ]
}
```

`.vscode/launch.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/mfussenegger/dapconfig-schema/master/dapconfig-schema.json",
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Listen for Xdebug",
      "type": "php",
      "request": "launch",
      "port": 9003
    },
    {
      "name": "Built-in Server with Xdebug",
      "type": "php",
      "request": "launch",
      "runtimeArgs": [
        "-S", "localhost:8080"
      ],
      "port": 9003
    }
  ]
}
```

`.user.ini` (per-directory php ini configuration file):
```ini
xdebug.mode=debug
xdebug.client_host=0.0.0.0
xdebug.client_port=9003
xdebug.start_with_request=yes
xdebug.idekey=NEOVIM
```

### For CLI App
Here is running order for CLI App:
1. Add breakpoint in `App.php`
2. Run the *Listen for Xdebug* from launch configuration
3. Run the cli with command: `XDEBUG_CONFIG="idekey=NEOVIM" php -c .user.ini ./vendor/bin/phpunit src/App.php`
### For Server App
It is much more simple to run server app:
1. Add breakpoint in `index.php`
2. Run *Built-in Server with Xdebug*
3. Trigger breakpoint by sending request to the corresponding routing/endpoint.
### Notes
I am not sure why the server is not shutting down when I stop the debugger for server app, I will need to figure out later, but a workaround for this is to manually kill the server with this command:
```shell
sudo kill -9 $(lsof -t -i tcp:8080)
```
