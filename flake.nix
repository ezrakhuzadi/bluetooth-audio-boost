{
  description = "GTK4 app and CLI to monitor PipeWire Bluetooth codecs with optional SBC high-bitpool rebuild";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = false;
        };

        lib = pkgs.lib;
        pythonPackages = pkgs.python3Packages;

        bluetooth-bitrate-manager = pythonPackages.buildPythonApplication rec {
          pname = "bluetooth-bitrate-manager";
          version = "0.1.0";

          pyproject = true;
          src = self;

          nativeBuildInputs = with pkgs; [
            pythonPackages.setuptools
            pythonPackages.wheel
            pkg-config
            gobject-introspection
            wrapGAppsHook4
          ];

          propagatedBuildInputs = [
            pythonPackages.pygobject3
          ];

          buildInputs = with pkgs; [
            gtk4
            libadwaita
            glib
            shared-mime-info
            adwaita-icon-theme
            pipewire
            wireplumber
          ];

          # Ensure CLI helpers referenced by the GUI (pactl, git, meson, etc.)
          # stay accessible when the wrapped binaries run.
          gappsWrapperArgs = let
            runtimePath = lib.makeBinPath [
              pkgs.pulseaudio
              pkgs.pipewire
              pkgs.wireplumber
              pkgs.git
              pkgs.meson
              pkgs.ninja
              pkgs.gcc
              pkgs.pkg-config
              pkgs.curl
              pkgs.coreutils
              pkgs.findutils
              pkgs.gawk
              pkgs.gnugrep
              pkgs.gnused
              pkgs.util-linux
            ];
          in [
            "--prefix" "PATH" ":" runtimePath
          ];

          postInstall = ''
            install -Dm644 $src/LICENSE \
              $out/share/licenses/bluetooth-bitrate-manager/LICENSE
            install -Dm644 bluetooth_bitrate_manager/resources/bluetooth-bitrate-manager.desktop \
              $out/share/applications/bluetooth-bitrate-manager.desktop
          '';

          meta = with lib; {
            description = "GTK4 application and CLI to monitor PipeWire Bluetooth codecs with optional high-bitpool SBC rebuild";
            homepage = "https://github.com/ezrakhuzadi/bluetooth-bitrate-manager";
            license = licenses.mit;
            maintainers = [];
            mainProgram = "bluetooth-bitrate-manager";
            platforms = platforms.linux;
          };
        };
      in {
        packages = {
          bluetooth-bitrate-manager = bluetooth-bitrate-manager;
          default = bluetooth-bitrate-manager;
        };

        apps = {
          bluetooth-bitrate-manager = {
            type = "app";
            program = "${bluetooth-bitrate-manager}/bin/bluetooth-bitrate-manager";
            meta = {
              description = "Launch the Bluetooth Bitrate Manager GTK interface";
            };
          };
          default = {
            type = "app";
            program = "${bluetooth-bitrate-manager}/bin/bluetooth-bitrate-manager";
            meta = {
              description = "Launch the Bluetooth Bitrate Manager GTK interface";
            };
          };
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ bluetooth-bitrate-manager ];
          nativeBuildInputs = with pkgs; [
            git
            meson
            ninja
            curl
          ];
        };
      }
    );
}
