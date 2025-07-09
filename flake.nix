{
  description = "Python SQLAlchemy + Alembic project with PostgreSQL";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          sqlalchemy
          alembic
          psycopg2
          python-dotenv
          python-dateutil
          pytest
          pytest-asyncio
          black
          flake8
          mypy
          isort
          boto3
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            postgresql
            docker
            docker-compose
            gnumake
          ];

          shellHook = ''
            echo "🐍 Python SQLAlchemy + Alembic Development Environment"
            echo "📦 Python version: $(python --version)"
            echo "🗄️  PostgreSQL version: $(postgres --version)"
            echo "🐳 Docker version: $(docker --version)"
            echo ""
            echo "Available commands:"
            echo "  make help                       - Show available make targets"
            echo "  make db-up                      - Start PostgreSQL container"
            echo "  make db-down                    - Stop PostgreSQL container"
            echo "  make db-reset                   - Reset database (stop, remove, start)"
            echo "  make test-lambda                - Test Lambda function locally (all migrations)"
            echo "  make test-lambda-to TARGET=002  - Test Lambda to specific revision"
            echo "  make list-migrations            - List available migrations"
            echo "  make clean                      - Clean temporary files"
            echo ""
            
            # Set environment variables
            export DATABASE_URL="postgresql://alembic_user:alembic_pass@localhost:5432/alembic_db"
            export PYTHONPATH="${pythonEnv}/lib/python3.11/site-packages:$PYTHONPATH"
          '';
        };

        packages.default = pythonEnv;
      });
}
