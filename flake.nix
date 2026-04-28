{
  description = "Mini Observable K8s Platform – Nix development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        pythonEnv = python.withPackages (ps: with ps; [
          fastapi
          uvicorn
          sqlalchemy
          psycopg2
          prometheus-client
          pydantic
          httpx
          pytest
          pytest-asyncio
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.docker
            pkgs.docker-compose
            pkgs.kubectl
            pkgs.kind
            pkgs.gnumake
            pkgs.curl
            pkgs.jq
          ];

          shellHook = ''
            echo "Mini Observable K8s Platform – dev shell ready"
            echo "Python: $(python --version)"
            echo "kubectl: $(kubectl version --client --short 2>/dev/null || true)"
            echo "kind:    $(kind version 2>/dev/null || true)"
            echo ""
            echo "Run 'make help' for available targets."
          '';
        };
      }
    );
}
