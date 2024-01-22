import subprocess
import os
import requests

def get_gitlab_version():
    try:
        current_version = subprocess.check_output("dpkg -l | grep gitlab-ce | awk '{print $3}'", shell=True, text=True).strip()
        return current_version
    except subprocess.CalledProcessError:
        print("Error al obtener la versión actual de GitLab.")
        return None

def install_gitlab_package(package_path):
    try:
        os.system(f"sudo dpkg -i {package_path}")
        os.system("sudo apt-get install -f")  # Instalar dependencias faltantes si las hay
        return True
    except Exception as e:
        print(f"Error durante la instalación del paquete: {e}")
        return False

def download_package(download_url, package_path):
    try:
        response = requests.get(download_url, allow_redirects=True)
        if response.status_code == 200:
            with open(package_path, 'wb') as f:
                f.write(response.content)
            return True
        elif response.status_code == 404:
            print("La versión solicitada no existe.")
            return False
        else:
            print(f"Error al descargar el paquete. Código de respuesta: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error al descargar el paquete: {e}")
        return False

def main():
    current_version = get_gitlab_version()
    if current_version is None:
        return

    print(f"Versión actual de GitLab: {current_version}")

    version_parts = current_version.split('.')
    version_numbers = [int(part) if part.isdigit() else part for part in version_parts]

    # Variable para contar las iteraciones
    iteration_count = 0

    while iteration_count < 12:
        version_numbers[1] += 1
        next_version = ".".join(map(str, version_numbers))

        print(f"Iteración {iteration_count + 1}: Descargando e instalando versión: {next_version}")

        download_url = f"https://packages.gitlab.com/gitlab/gitlab-ce/packages/debian/buster/gitlab-ce_{next_version}_amd64.deb/download.deb"

        print(f"Descargando desde: {download_url}")

        package_path = f"/tmp/gitlab-ce_{next_version}.deb"
        download_success = download_package(download_url, package_path)

        if not download_success:
            # La descarga ha fallado, pero ahora se verifica si fue un error 404
            iteration_count += 1  # Incrementar el contador
            continue

        install_success = install_gitlab_package(package_path)

        if not install_success:
            print("La instalación del paquete ha fallado. Continuando con la siguiente versión.")
            iteration_count += 1  # Incrementar el contador
            continue

        # Verificar si hay una nueva versión instalada
        new_version = get_gitlab_version()

        # Si la nueva versión es la misma que la actual, salta al siguiente ciclo del bucle
        if new_version == current_version:
            print(f"Versión {next_version} ya instalada. Continuando con la siguiente versión.")
            iteration_count += 1  # Incrementar el contador
            continue

        if new_version == current_version:
            print("No hay nuevas versiones disponibles.")
            break

        current_version = new_version
        iteration_count += 1  # Incrementar el contador

if __name__ == "__main__":
    main()
