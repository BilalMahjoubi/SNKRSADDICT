<?php
include_once('Fonctions.php');
$link = connectDB();

$user = $_POST['user'];
$nom = $_POST['nameD'];
$mdp = $_POST['mdp'];

$sql = "INSERT INTO `Login`(`user`, `nomDiscord`, `mdp`) VALUES ('".addslashes($user)."', '".addslashes($nom)."', '".addslashes($mdp)."')";
$result = $link->query($sql);

$monfichier = fopen('BOT/SNKRS/user.csv', 'c+');

// Tronquer le fichier à la taille zéro.
// Est équivalant à écraser le fichier

$list = array (array($user, $nom, $mdp));

fopen($monfichier,'w');

if($monfichier!=false)
{
    foreach ($list as $fields) {
        fputcsv($monfichier, $fields);
    }
    fclose($monfichier);
}else{
    print "Impossible d'ouvrir ou de créer le fichier.";
}

$output = shell_exec('python /Applications/MAMP/htdocs/Projet/NoSql/Script_python/SNKRSMonitor.py');

echo $output;

echo "OK";
