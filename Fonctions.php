<?php
function connectDB(){
    try {
        $db = new PDO('mysql:host=localhost;dbname=NoSql;charset=utf8', 'root', 'root');
        return $db;
    } catch (Exception $e) {
        die('Erreur : ' . $e->getMessage());
    }
}

function getShoes(){
    $link = connectDB();
    $req = $link->query('SELECT * FROM Nike WHERE brand LIKE "Nike%" ORDER BY id DESC');
    return $req;
}

function getBrand(){
    $link = connectDB();
    $req = $link->query('SELECT Brand FROM Sneakers GROUP BY Brand ORDER BY Brand ASC');
    return $req;
}

function getBestPrice($model){
    $link = connectDB();
    $req = $link->query("SELECT price FROM stockX where Model='".$model."'");
    $data = $req->fetch();
    if($data == ""){
        $req = $link->query("SELECT price FROM sneakers where Model='".$model."'");
        $data = $req->fetch();
        if($data == ""){
            $req = $link->query("SELECT price FROM nike where Model='".$model."'");
            $data = $req->fetch();

            return $data[0];
        }
        else{
            return $data[0];
        }
    }
    else{
        return $data[0];
    }

}


function getAllShoes($marque){
    $link = connectDB();
    $req = $link->query("SELECT * FROM Sneakers WHERE brand='".addslashes($marque)."' ORDER BY id DESC");
    return $req;
}

function get1Shoes(){
    $link = connectDB();
    $id = $_GET['id'];
    $req = $link->query("SELECT * FROM Nike WHERE id=".$id);
    return $req;
}

function get1ShoesBrand(){
    $link = connectDB();
    $id = $_GET['id'];
    $req = $link->query("SELECT * FROM Sneakers WHERE id=".$id);
    return $req;
}

function linkNike($model){
    $link = connectDB();
    $req = $link->query("SELECT * FROM Nike WHERE Model='".$model."'");
    $fetch = $req->fetch();
    return $fetch;
}

function linkSneakers($model){
    $link = connectDB();
    $req = $link->query("SELECT * FROM Sneakers WHERE Model='".$model."'");
    $fetch = $req->fetch();
    return $fetch;
}

function linkStockX($model){
    $link = connectDB();
    $req = $link->query("SELECT * FROM StockX WHERE Model='".$model."'");
    $fetch = $req->fetch();
    return $fetch;
}