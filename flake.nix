{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      checks = {
        pre-commit-check = pre-commit-hooks.lib.${system}.run {
          src = ./.;
          hooks = {
            typos.enable = true; # Source code spell checker
            prettier.enable = true; # Markdown & TS formatter
          };
          settings = {
            typos = {
              write = true; # Automatically fix typos
              configPath = "./.typos.toml";
            };
            prettier = {
              write = true; # Automatically format files
              configPath = "./.prettierrc.yaml";
            };
          };
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          # spell checker
          typos
          # code formatter
          nodePackages.prettier
        ];

        shellHook = ''
          ${self.checks.${system}.pre-commit-check.shellHook}
        '';
      };
    });
}
