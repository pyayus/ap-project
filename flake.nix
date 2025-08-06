{
  inputs = {
    nixpkgs.url = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonWithPackages = pkgs.python3.withPackages (
          python-pkgs: with python-pkgs; [
            python-lsp-server
            
            flask
            flask-sqlalchemy
            flask-wtf
            flask-login
          ]
        );
      in
      rec {
        packages.default = pkgs.writeShellScriptBin "serve-start" ''
          ${pythonWithPackages}/bin/python -m flask run
        '';

        devShell = pkgs.mkShell {
          packages = [ pythonWithPackages packages.default pkgs.ruff ];
        };
      }
    );
}
