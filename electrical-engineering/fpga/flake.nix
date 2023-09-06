{
  description = "tang nano 9k - development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    utils,
    ...
  }:
    utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          python311Packages.apycula # gowin fpga
          yosys # fpga synthesis
          nextpnr # fpga place and route

          # flash into fpga may need to set udev rules for usb device:
          # https://github.com/trabucayre/openFPGALoader/blob/master/99-openfpgaloader.rules
          openfpgaloader # fpga programming
        ];
      };
    });
}
