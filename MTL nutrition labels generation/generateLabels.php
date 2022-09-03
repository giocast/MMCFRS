<?php

//The following code generates Multiple Traffic Lights (MTL) nutritional labels by acquiring and computing information from each dish web page on allrecipes.com. This code uses the dom-to-image JS library to convert and download the final label images.

if(isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on')   
         $url = "https://";   
else  
    $url = "http://";   
    // Append the host(domain name, ip) to the URL.   
    $url.= $_SERVER['HTTP_HOST'];   
    
    // Append the requested resource location to the URL   
    $url.= $_SERVER['REQUEST_URI'];    
      
    echo $url; 

$components = parse_url($url);
parse_str($components['query'], $params);
 
$categ = $params['categ'];
$cont = $params['cont'];
$nameDish = str_replace("*", "'", $params['name']);
$servings = $params['servings'];
$servingSize = $params['servingSize'];
$caloriesKcal = $params['kcal'];
$caloriesKj = $params['kj'];
$sugar = $params['sugar'];
$fat = $params['fat'];
$satFat = $params['satfat'];
$salt = $params['salt'];
$sugar100 = $params['sugar100'];
$fat100 = $params['fat100'];
$satFat100 = $params['satfat100'];
$salt100 = $params['salt100'];


$coloreSugar = "";
$coloreFat = "";
$coloreSatFat = "";
$coloreSalt = "";

$livelloSugar = "";
$livelloFat = "";
$livelloSatFat = "";
$livelloSalt = "";


if($sugar100<=5) {
	$coloreSugar = "#9aca27"; //green
	$livelloSugar = "Low";
} else if ($sugar100>5 && $sugar100<=22.5) {
	$coloreSugar = "#fcbd00"; //yellow
	$livelloSugar = "Medium";
	}
	else if ($sugar100>22.5) {
		$coloreSugar = "#fc0d1b"; //red
		$livelloSugar = "High";
	}


if($fat100<=3) {
	$coloreFat = "#9aca27"; //green
	$livelloFat = "Low";
} else if ($fat100>3 && $fat100<=17.5) {
	$coloreFat = "#fcbd00"; //yellow
	$livelloFat = "Medium";
	}else if ($fat100>17.5) {
		$coloreFat = "#fc0d1b"; //red
		$livelloFat = "High";
	}


if($satFat100<=1.5) {
	$coloreSatFat = "#9aca27"; //green
	$livelloSatFat = "Low";
} else if ($satFat100>1.5 && $satFat100<=5) {
	$coloreSatFat = "#fcbd00"; //yellow
	$livelloSatFat = "Medium";
	}else if ($satFat100>5) {
		$coloreSatFat = "#fc0d1b"; //red
		$livelloSatFat = "High";
	}



if($salt100<=0.3) {
	$coloreSalt= "#9aca27"; //green
	$livelloSalt = "Low";
} else if ($salt100>0.3 && $salt100<=1.5) {
	$coloreSalt = "#fcbd00"; //yellow
	$livelloSalt = "Medium";
	}else if ($salt100>1.5) {
		$coloreSalt = "#fc0d1b"; //red
		$livelloSalt = "High";
	}

 
$salt = number_format($salt, 2, '.', '');
if(fmod($salt, 1) == 0.00){
    $salt = round($salt, 0);
}
   

$lunghTesto = strlen($nameDish);
if($lunghTesto>39) {

	if($lunghTesto<55) {
		$dimTesto = "15px";
		$marginTesto = "2.75px";
	} else {

	$dimTesto = "15px";
	$marginTesto = "-5.75px";

	}
}
else {
	$dimTesto = "20px";
	$marginTesto = "0px";
}


echo "

<html>
<head>
    <script src='https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js'></script>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js'></script>
    <script src='dom-to-image.js'></script>
</head>

<body style='border: 1px solid #808080; width: 500px; height: 300px'>
    <div id='html-content-holder' style='background-color: white; color: black; width: 414px; padding: 0px; font-family: arial; padding-top: 22px;padding-bottom: 22px'>
    	<center>
    		<p style='font-size: ".$dimTesto."; padding: 0px; margin:".$marginTesto.";margin-left:0px;margin-right:0px;width:414px;word-wrap: break-word;text-align:center'><b> ".$nameDish." </b></p><br>
	    	<div style='background-color: transparent; width: 400px; display:flex; '>
	    		<div style='float: left; margin-left:75px; background-color:transparent;'><span style='font-size:17px'><b>Servings</b></span><br><span style='font-size:17px'><b>".$servings."</b></span></div>
	    		<div style='margin-left: 60px; background-color:transparent; width:300px;'><span style='font-size:17px; width:20px'><b>Serving size</b></span><br><span style='font-size:17px'><b>".$servingSize." (g)</b></span></div>
	    	</div>
	    	<br>

	    	<div style='background-color: transparent; width: 400px; height: 140px; display:flex; padding: 5px'>
	    		
	    		<div style='background-color:white; width: 90px; height: 100px; margin-left: 2px; border-radius: 38px 38px 38px 38px; padding-top: 20px; border: 2px solid black;'>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 0px;margin-top: -3px;background-color: white;border-radius: 25px;width: 50px;padding: 4px;padding-left: 5px;padding-right: 5px;display: block;border: 2px solid black;'>Energy</div>
	    			<span style='font-size: 16px;font-weight: bold;position: relative;top: 8px;margin-top: -3px;background-color: white;border-radius: 25px;width: 70px;padding: 4px;display: block;'>".$caloriesKcal." Kcal</span>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 13px;background-color: white;padding: 4px;border-radius: 25px;width: 60px;display: block;margin-bottom: 0px;'>".round($caloriesKj)." Kj</div>
	    		</div>
	    		<div style='background-color:".$coloreSugar."; width: 90px; height: 100px; margin-left: -2px; border-radius: 38px 38px 38px 38px; padding-top: 20px; border: 2px solid black;'>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 0px;margin-top: -3px;background-color: white;border-radius: 25px;width: 50px;padding: 4px;display: block;border: 2px solid black;'>Sugar</div>
	    			<span style='font-size: 16px;font-weight: bold;position: relative;top: 2px;background-color: white;padding: 4px;border-radius: 25px;width: 50px;display: block;margin-bottom: 0px;border: 2px solid black;'>".$sugar."</span>
	    			<div style='border-top: 2px solid black;top: 6.2px;position: relative;padding-top: 3px;font-size: 16px;font-weight: bold;background: white;border-bottom-left-radius: 51px;border-bottom-right-radius: 51px;height: 31px;width: 77px;color: ".$coloreSugar.";'>".$livelloSugar."</div>
	    		</div>
	    		<div style='background-color:".$coloreFat."; width: 90px; height: 100px; margin-left: -2px; border-radius: 38px 38px 38px 38px; padding-top: 20px; border: 2px solid black;'>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 0px;margin-top: -3px;background-color: white;border-radius: 25px;width: 50px;padding: 4px;display: block;border: 2px solid black;'>Fat</div>
	    			<span style='font-size: 16px;font-weight: bold;position: relative;top: 2px;background-color: white;padding: 4px;border-radius: 25px;width: 50px;display: block;margin-bottom: 0px;border: 2px solid black;'>".$fat."</span>
	    			<div style='border-top: 2px solid black;top: 6.2px;position: relative;padding-top: 3px;font-size: 16px;font-weight: bold;background: white;border-bottom-left-radius: 51px;border-bottom-right-radius: 51px;height: 31px;width: 77px;color: ".$coloreFat.";'>".$livelloFat."</div>
	    		</div>
	    		<div style='background-color:".$coloreSatFat."; width: 90px; height: 100px; margin-left: -2px; border-radius: 38px 38px 38px 38px; padding-top: 20px; border: 2px solid black;'>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 0px;margin-top: -3px;background-color: white;border-radius: 25px;width: 55px;padding: 4px;display: block;border: 2px solid black;'>Sat Fat</div>
	    			<span style='font-size: 16px;font-weight: bold;position: relative;top: 2px;background-color: white;padding: 4px;border-radius: 25px;width: 55px;display: block;margin-bottom: 0px;border: 2px solid black;'>".$satFat."</span>
	    			<div style='border-top: 2px solid black;top: 6.2px;position: relative;padding-top: 3px;font-size: 16px;font-weight: bold;background: white;border-bottom-left-radius: 51px;border-bottom-right-radius: 51px;height: 31px;width: 77px;color: ".$coloreSatFat.";'>".$livelloSatFat."</div>
	    		</div>
	    		<div style='background-color:".$coloreSalt."; width: 90px; height: 100px; margin-left: -2px; border-radius: 38px 38px 38px 38px; padding-top: 20px; border: 2px solid black;'>
	    			<div style='font-size: 16px;font-weight: bold;position: relative;top: 0px;margin-top: -3px;background-color: white;border-radius: 25px;width: 50px;padding: 4px;display: block;border: 2px solid black;'>Salt</div>
	    			<span style='font-size: 16px;font-weight: bold;position: relative;top: 2px;background-color: white;padding: 4px;border-radius: 25px;width: 50px;display: block;margin-bottom: 0px;border: 2px solid black;'>".$salt."g</span>
	    			<div style='border-top: 2px solid black;top: 6.2px;position: relative;padding-top: 3px;font-size: 16px;font-weight: bold;background: white;border-bottom-left-radius: 51px;border-bottom-right-radius: 51px;height: 31px;width: 77px;color: ".$coloreSalt.";'>".$livelloSalt."</div>
	    		</div>

	    	</div>

	    	<span style='font-weight: bold; font-size: 13px; position: relative; top: -9px;'>* Nutritional content per serving, of an adult's reference intake</span>

    	</center>

    </div>
    <script>
        
    function staccaStacca() {
  		self.close();
	}

	

	$(document).ready(function () {
        
		domtoimage.toJpeg(document.getElementById('html-content-holder'), { scale: 4 })
    .then(function (dataUrl) {
        var link = document.createElement('a');
        link.download = '".$categ."-".$cont."-".str_replace("'", "^", $nameDish).".jpeg';
        link.href = dataUrl;
        link.click();


        self.close()
        //const myTimeout = setTimeout(staccaStacca, 5000);



        
    });
});
	    

    </script>
</body>
</html> 	";		


?>