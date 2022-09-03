<?php


$myfile = fopen("snack_500_rev_3.csv", "r");
$cont = 1;
while (!feof($myfile)) {
    $line = fgets ($myfile);
    $linea = explode(";", $line);
    //print_r($lineA);
    //echo json_encode($arr);

    $categ=$linea[1];
    $nameDish=$linea[3];
    $servings=$linea[6];
    $servingSize=$linea[16];
    $caloriesKcal=$linea[4]; //then perform equivalent in Kj
    $sugar=$linea[10];
    $fat=$linea[11];
    $satFat=$linea[12];
    $salt=$linea[24];

    //for coloring
    $sugar100=$linea[20];
    $fat100=$linea[21];
    $satFat100=$linea[22];
    $salt100=$linea[25];


    /*foreach ($lineA as $value) {
        echo $value . ' ';

    }*/

    //echo "<script>myTimeout = setTimeout(function() { window.open('generateLabels.php?a=1'); }, 5000);</script>";

    $nameDish = str_replace("'", "*", $nameDish);
    $url = "generateLabels.php?categ=".$categ."&cont=".$cont."&name=".$nameDish."&servings=".$servings."&servingSize=".$servingSize."&kcal=".$caloriesKcal."&kj=".floatval($caloriesKcal)*4.186."&sugar=".$sugar."&fat=".$fat."&satfat=".$satFat."&salt=".$salt."&sugar100=".$sugar100."&fat100=".$fat100."&satfat100=".$satFat100."&salt100=".$salt100;
    echo $url; 

    $myArr = [105];

    if (in_array($cont, $myArr)) {
    echo "<script>window.open('".$url."');</script>";
    }
	/*if($cont==1) {

		break;
	}*/

	$cont+=1;




}
fclose ($myfile);

/*
 # 0   ID              http://allrecipes.com/recipe/salmon-croquettes/detail.aspx;
        # 1   CATEG           Snack;
        # 2   IMAGE           http://images.media-allrecipes.com/userphotos/250x250/00/40/85/408546.jpg;
        # 3   NAME            Salmon Croquettes;
        # 4   CAL KCAL        435;
        # 5   INGRED          salmon,egg,celery,onion,weed,garlic,olive oil;
        # 6   SERVINGS        2;
        # 7   PROTEIN         27.9g;
        # 8   CARB            12.2g;
        # 9   FIBER           3.2g;
        # 10  SUGAR           0.9g;
        # 11  FAT             30.9g;
        # 12  SAT FAT         5.2g;
        # 13  SODIUM          359.5mg;
        # 14  FSA_OLD         5;
        # 15  TOT GRAM WEIG   361.047104
        # 16 serving size
        # 17 protein100
        # 18 carb100
        # 19 fiber100
        # 20 sugar100
        # 21 fat100
        # 22 satfat100
        # 23 sodium100
        # 24 saltG
        # 25 salt100
        # 26 kj100
        # 27 nutriscore
        # 28 FSAnew

        #  ]
        #
        #   *********** FSA add SOON
       
*/




?>