---
layout: post
title:  "Debugging PHP App in NeoVim with Launch Configuration"
date:   2025-05-06 06:00:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
---


私は時々、2つの異なる状況でPHPコードをデバッグする必要があります。1つはCLI（コマンドライン）アプリで、もう1つはWebサーバーアプリです。それぞれの実行方法は少し異なりますが、手順は微妙であり、正しい順番をよく忘れてしまいます。

### NeoVimプラグイン
- `mfussenegger/nvim-dap`
- `kristijanhusak/vim-dadbod-ui`

### プロジェクトディレクトリ構成
このようなプロジェクトディレクトリ構成を想定します:
```
src
└── App.php -- CLIアプリのエントリーポイント
index.php   -- サーバーアプリのエントリーポイント
composer.json
flake.nix   -- Nix flake ファイル (NixOS)
.user.ini   -- PHP ini 設定ファイル
.vscode
└── launch.json -- Launch configuration
```

私は現在、各プロジェクトの環境をセットアップするためにNixパッケージマネージャーを使用しています。Nixを使うと、必要なPHP拡張を有効化・追加できるため、PHP環境のセットアップが非常に便利です。今回必要なのは`xdebug`拡張です。

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
````

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

`.user.ini`（ディレクトリごとのphp ini設定ファイル）:
```ini
xdebug.mode=debug
xdebug.client_host=0.0.0.0
xdebug.client_port=9003
xdebug.start_with_request=yes
xdebug.idekey=NEOVIM
```

### CLIアプリの場合
CLIアプリを実行する順番は以下の通りです:
1. `App.php` にブレークポイントを追加する
2. Launch configurationから *Listen for Xdebug* を実行する
3. 次のコマンドでCLIを実行する:

   ```shell
   XDEBUG_CONFIG="idekey=NEOVIM" php -c .user.ini ./vendor/bin/phpunit src/App.php
   ```

### サーバーアプリの場合
サーバーアプリの実行はよりシンプルです:
1. `index.php` にブレークポイントを追加する
2. *Built-in Server with Xdebug* を実行する
3. 対応するルーティング/エンドポイントにリクエストを送信し、ブレークポイントをトリガーする

### 注意点
サーバーアプリのデバッガを停止したときに、サーバーが終了しない理由はまだ分かっていません。現時点での回避策は、次のコマンドで手動でサーバーを強制終了することです:
```shell
sudo kill -9 $(lsof -t -i tcp:8080)
```

