$id_visita = isset($_GET['id_visita']) ? $_GET['id_visita'] : [id_visita];

// Definición de rutas según el entorno (Mantenemos tu lógica AMP)
if($_SERVER['SERVER_NAME'] == 'scriptcase.amp.gob.pa'){
    $ruta_base = $_SERVER['DOCUMENT_ROOT'] . "/scriptcase/app/VISITANTES/_lib/img/";
    $ruta_base_foto = $_SERVER['DOCUMENT_ROOT'] . "/scriptcase/file/img/foto_visitante/";
} else {
    $ruta_base = $_SERVER['DOCUMENT_ROOT'] . "/_lib/img/";
    $ruta_base_foto = $_SERVER['DOCUMENT_ROOT'] . "/_lib/file/img/foto_visitante/";
}

// Consultas a BD
$search_visits = "SELECT id_visitors, buildings_visited, uadm_visited, check_in FROM visits WHERE (id = '$id_visita') LIMIT 1";
sc_lookup(vs, $search_visits, "conn_mariadb");

if(!empty({vs})){
    $id_visitors       = {vs[0][0]};
    $buildings_visited = {vs[0][1]};
    $uadm_visited      = {vs[0][2]};
    $check_in          = date("d-M-Y h:i a", strtotime({vs[0][3]}));

    $search_visitor = "SELECT names, surnames, id_card_number, photo FROM visitors WHERE (id = '$id_visitors') LIMIT 1";
    sc_lookup(vt, $search_visitor, "conn_mariadb");

    $nombre_visitor = !empty({vt}) ? {vt[0][0]}. ' ' .{vt[0][1]} : "N/A";
    $id_card_number = !empty({vt}) ? {vt[0][2]} : "";
    $photo          = !empty({vt}) ? {vt[0][3]} : "";

    // VALIDACIÓN PARA EVITAR ERROR "Path cannot be empty"
    $visitante_foto = (!empty($photo) && file_exists($ruta_base_foto . $photo)) ? $ruta_base_foto . $photo : "";
    $logo_amp = $ruta_base . "grp__NM__img__NM__logo_negro_blanco.png";

    $uadm_visited_array = explode(";", $uadm_visited);

    ob_start();
    ?>
    <style>
        /* Configuración para 2x4" (57.15mm x 101.6mm) */
        .ticket-wrapper { width: 100%; height:98mm; font-family: Arial, sans-serif; padding: 0; margin: 0; position: relative; }

		/* Cabecera */
        .header-section { width: 100%; text-align: center; margin-top: 1.5mm; padding-bottom: 1mm; margin-bottom: 1mm; }
        .text-h1 { font-size: 12pt; font-weight: bold; }
        .text-cedula { font-size: 10pt; font-weight: bold; }
        .text-fecha { font-size: 8pt; font-weight: bold; }

        .section-title { font-size: 7.5pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px; }
        .uadm-text { font-size: 7pt; line-height: 1.1; margin-top: 1mm; font-weight: bold; margin-bottom: 2mm;}

		/* Tabla de Edificios: Ahora ocupa el 100% de su columna */
        .edificios-table { width: 100%; margin: 0 auto; border: 1px solid #000; }
        .edificios-table th { font-size: 8pt; border: 1px solid #000; background-color: #f0f0f0; width: 14.2%; text-align: center; }
        .edificios-table td { height: 18px; border: 1px solid #000; text-align: center; }

		/* Tabla QR y Logo */
		.qr-logo-table {width: 100%; border-collapse: collapse; border-style: none; margin-left: auto; margin-right: auto; margin-top: 5px;}
		.qr-td {width: 50%; vertical-align: middle;}
		.logo-td {width: 50%; text-align: right; vertical-align: middle;}
        .logo-amp-small { width: 14mm; margin-top: 1mm; }

		/* Footer texto */
		.visit-ticket { width: 100%; height: 20px; background-color: #000; color: #fff; text-align: center; vertical-align: middle; border-radius: 10px; }
		.text-visitante { font-size: 25px; font-weight: bold; }
		.footer-fix { position: absolute; bottom: 0; width: 100%; border-top: 0.5px solid #000; }
    </style>

    <page backtop="1mm" backbottom="0" backleft="2mm" backright="2mm">
        <div class="ticket-wrapper">

            <div class="header-section">
                <span class="text-h1"><?php echo mb_strtoupper($nombre_visitor); ?></span><br>
                <span class="text-cedula">CED: <?php echo $id_card_number; ?></span><br>
				<span class="text-fecha" ><?php echo $check_in; ?></span>
            </div>

			<div class="section-title">UNIDAD ADMINISTRATIVA VISITADA</div>
			<div class="uadm-text">
				<?php

				foreach ($uadm_visited_array as $uadm){
					sc_lookup(uadm_data, "select nombre from unidades_administrativas_bienes where id = '$uadm' limit 1", "conn_mariadb_1");
					if(!empty({uadm_data})) echo "• " . {uadm_data[0][0]} . "<br>";
				}
				?>
			</div>

			<div class="section-title">EDIFICIOS AUTORIZADOS</div>
			<table class="edificios-table">
				<tr>
					<th>1</th>
					<th>2</th>
					<th>3</th>
					<th>4</th>
					<th>5</th>
					<th>6</th>
					<th>P</th>
				</tr>
				<tr>
					<?php for($i=1; $i<=7; $i++): ?>
						<td style="<?php if(str_contains($buildings_visited, (string)$i)) echo 'background-color:black;'; ?>"></td>
					<?php endfor; ?>
				</tr>
			</table>

			<table class="qr-logo-table ">
				<tbody>
					<tr>
						<td class="qr-td">
							<qrcode value="<?php echo $id_visita; ?>" ec="L" style="width: 16mm;"></qrcode>
						</td>

						<td class="logo-td">
							<img src="<?php echo $logo_amp; ?>" class="logo-amp-small">
						</td>
					</tr>
				</tbody>
			</table>

			<div class="footer-fix visit-ticket">
				<span class="text-visitante">V I S I T A N T E</span>
			</div>
		</div>

    </page>

    <?php
    $html = ob_get_clean();
    sc_include_library('prj', 'html2pdf', 'html2pdf/autoload.php');

    // 'L' para Landscape, asegurando que use los 101.6mm del rodillo
    $html2pdf = new Spipu\Html2Pdf\Html2Pdf('P', array(57, 101), 'es', true, 'UTF-8', array(0, 0, 0, 0));
    $html2pdf->writeHTML($html);
    $html2pdf->pdf->IncludeJS("print(true);");
    $html2pdf->output("Etiqueta_AMP.pdf", 'I');

}else{
	?>
	<!DOCTYPE html>
	<html lang="es">

	<head>
		<meta charset="UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Template - Boostrap</title>
		<!-- Favicon icon -->
		<link rel="icon" href="img/favicon.png" type="image/x-icon">

		<!-- Recursos -->


		<!-- Bootstrap -->
		<link rel="stylesheet" href="https://bootswatch.com/5/flatly/bootstrap.min.css">

		<!-- Material Icons -->
		<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">

		<!-- CSS -->
		<link rel="stylesheet" href="vendor/css/main.css">

	</head>

	<body>
		<div class="container">
			<div class="text-center mt-2">
				<div class="alert alert-dismissible alert-warning">
					<h4 class="alert-heading">Warning!</h4>
					<p class="mb-0">La visita que busca no exite.</p>
				</div>
			</div>

		</div>
	</body>
	</html>
	<?php

}
