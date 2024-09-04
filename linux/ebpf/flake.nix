{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/master";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          (python311.withPackages (ps:
            with ps; [
              bcc
            ]))
        ];

        shellHook = ''
          python --version
        '';
      };
    });
}
