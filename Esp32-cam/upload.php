<?php
$uploaddir = '/var/www/html/cam_images/';
$uploadfile = $uploaddir . time() . '.jpg';

$input = file_get_contents('php://input');

if (file_put_contents($uploadfile, $input)) {
    echo "Archivo guardado correctamente.";
} else {
    echo "Error al guardar el archivo.";
}
?>
