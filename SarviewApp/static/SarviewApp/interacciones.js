function registrar() {
    alert("Solo los usuarios registrados pueden dar de alta a nuevos participantes. Una vez iniciada la sesión te enviará a la página de registro.");
}
function abrir() {
    document.getElementById("main").style.marginLeft = "10%";
    document.getElementById("mySidebar").style.width = "10%";
    document.getElementById("mySidebar").style.display = "block";
    document.getElementById("openNav").style.display = 'none';
}
function cerrar() {
    document.getElementById("main").style.marginLeft = "0%";
    document.getElementById("mySidebar").style.display = "none";
    document.getElementById("openNav").style.display = "inline-block";
}
function fechas() {
    var x = document.getElementById("desde").value;
    var y = document.getElementById("hasta").value;
    alert("Se cargarán los datos desde: " + x + " Hasta: " + y +".\nEn caso de no ser posible se sobreeescribirán por datos adecuados o los últimos disponibles.")
}