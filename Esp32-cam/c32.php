<?php
// Configuración de la contraseña
$password = 'ñorenji01!'; // Cambia esto por la contraseña que desees usar

// Verificar la autenticación
if (!isset($_SERVER['PHP_AUTH_USER']) || $_SERVER['PHP_AUTH_PW'] != $password) {
    header('WWW-Authenticate: Basic realm="Acceso restringido"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Acceso denegado';
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Imágenes de la Cámara</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Últimas 6 imágenes</h1>
        <div class="row">
            <?php
            $dir = '/var/www/html/cam_images/';
            $files = scandir($dir);
            $images = array_filter($files, function($file) {
                return preg_match('/\.(jpg|jpeg|png|gif)$/i', $file);
            });
            arsort($images);
            $latest_6 = array_slice($images, 0, 6);

            foreach ($latest_6 as $image) {
                echo '<div class="col-md-4 mb-4">';
                echo '<img src="/cam_images/' . $image . '" class="img-fluid" alt="' . $image . '">';
                echo '</div>';
            }
            ?>
        </div>

        <h2 class="mt-4">Listado de los últimos 20 archivos</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Nombre del archivo</th>
                    <th>Fecha de creación</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $all_files = array();
                foreach ($files as $file) {
                    if ($file != "." && $file != "..") {
                        $all_files[$file] = filemtime($dir . $file);
                    }
                }
                arsort($all_files);
                $limited_files = array_slice($all_files, 0, 20, true);

                foreach ($limited_files as $file => $timestamp) {
                    echo '<tr>';
                    echo '<td><a href="/cam_images/' . $file . '" target="_blank">' . $file . '</a></td>';
                    echo '<td>' . date("Y-m-d H:i:s", $timestamp) . '</td>';
                    echo '</tr>';
                }
                ?>
            </tbody>
        </table>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
