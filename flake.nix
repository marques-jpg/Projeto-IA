{
  description = "Ambiente de Desenvolvimento devenv para o Projeto de IA - Slitherlink";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    devenv.url = "github:cachix/devenv";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [ inputs.devenv.flakeModule ];
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      perSystem = { config, self', inputs', pkgs, system, ... }: {
        devenv.shells.default = {
          # Define a raiz para evitar erros de leitura na Nix Store
          devenv.root = 
            let
              envRoot = builtins.getEnv "PWD";
            in if envRoot != "" then envRoot else ./.;

          name = "slitherlink-ia-env";

          packages = with pkgs; [
            (python311.withPackages (ps: with ps; [
              numpy
              tkinter
            ]))
            tk
            tcl
          ];

          env.TK_LIBRARY = "${pkgs.tk}/lib/tk8.6";
          env.TCL_LIBRARY = "${pkgs.tcl}/lib/tcl8.6";

          enterShell = ''
            echo "🐍 Ambiente do Projeto Slitherlink Carregado!"
            echo "Versão do Python: $(python --version)"
            echo "Podes agora correr: python slitherlink_gui.py"
          '';
        };
      };
    };
}
