{
  description = "OIDC Demo Resouce Server Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};

    in
    {
      packages = {
        oidc-demo-app = pkgs.callPackage ./package.nix { };
        default = self.packages.${system}.oidc-demo-app;
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3.pkgs.uv
          python3.pkgs.ruff
        ];

        inputsFrom = [

        ];
      };

      formatter = pkgs.nixpkgs-fmt;
    });
}
