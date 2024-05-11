// -------------------------- VARIABLES --------------------------

console.log('hola')

// URL del servidor Flask
const flaskServerUrl = 'http://localhost:5555';

// Elementos de la dropzone
const dropzone = document.querySelector('.dropzone');
const btnSubirArchivo = document.getElementById('btnSubirArchivo');
const inputSubirArchivo = document.getElementById('inputSubirArchivo');
const dragText = dropzone.querySelector('h2');
const btnEnviarVideos = document.getElementById('btnEnviarVideos');
const cargando = document.getElementById('cargando');

// Elementos de la seccionAcciones
const seccionAcciones = document.getElementById('seccionAcciones');
const barraProgresoVideos = document.getElementById('barraProgresoVideos');
const textoProgreso = document.getElementById('textoProgreso');
const acciones = document.querySelectorAll('.accion');     // Encuentra todos los elementos con la clase 'accion'
const btnElegirAcciones= document.getElementById('btnElegirAcciones');

let files;
let ficheroAEnviar = null;
// let ruta_video_servidor = 'videos/791248b2-b2af-4cb3-957b-f738a2b71e9e.mkv';
// let ruta_json = 'json/791248b2-b2af-4cb3-957b-f738a2b71e9e.json';
let ruta_video_servidor;
let ruta_json;

// ----------------------- ANIMACION ENTRADA -----------------------

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        } else {
            entry.target.classList.remove('show');
        }
    });
});

const hiddenElements = document.querySelectorAll('.hidden');
hiddenElements.forEach((element) => {
    observer.observe(element);
});


// -------------------- FUNCIONES SUBIR ARCHIVO A DROPZONE ------------------------

btnSubirArchivo.onclick = (e) => {
    inputSubirArchivo.click();
};

inputSubirArchivo.addEventListener('change', (e) => {
    files = e.target.files;
    dropzone.classList.add('active');
    showFiles(files);
    dropzone.classList.remove('active');
});

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('active');
    dragText.textContent = 'Suelta el archivo para subirlo';
});

dropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropzone.classList.remove('active');
    dragText.textContent = 'Arrastra y suelta el vídeo';
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    files = e.dataTransfer.files;
    showFiles(files);
    dropzone.classList.remove('active');
    dragText.textContent = 'Arrastra y suelta el vídeo';
});

function showFiles(files) {
    if (files.length == undefined){
        processFile(files);
    }else{
        for (const file of files){
            processFile(file);
        }
    }
}

function processFile(file){

    const fileType = file.type;
    const validTypes = ['video/mp4', 'video/x-matroska'];

    if(!validTypes.includes(fileType)){
        muestraError('Formato no valido', 'errorzoneArchivo');
    }else if (ficheroAEnviar != null){
        muestraError('Max numero archivos', 'errorzoneArchivo');
    }else{
        let imgPathType;
        if (fileType == 'video/mp4'){
            imgPathType = 'imgs/mp4.png';
        }else{
            imgPathType = 'imgs/mkv.png';
        }

        let idBtn = 'btnEliminarArchivo';
        let htmlVideo = `
        <div class="video">
            <img class="archivoImg" src="${imgPathType}" alt="Archivo">
            <p class="archivoTexto">${file.name}</p>
            <button class="btnDropzone btnEliminarArchivo" id="${idBtn}" onclick="eliminarArchivo('${idBtn}')">Eliminar</button>
        </div>`;

        const html = document.querySelector('.videos').innerHTML;
        document.querySelector('.videos').innerHTML = html + htmlVideo;

        ficheroAEnviar = file;
        document.getElementById('btnEnviarVideos').classList.remove('oculto');
    }

}

// Elimina el archivo de la dropzone
function eliminarArchivo(idBtn){
    const btn = document.getElementById(idBtn);
    btn.parentElement.remove();

    document.getElementById('btnEnviarVideos').classList.add('oculto');

    ficheroAEnviar = null;
}

// Muestra un mensaje de error en seccionArchivo
function muestraError(error, idZona){
    let htmlError;
    switch (error){
        case 'Formato no valido':
            htmlError = `
            <div class="mensajeError">
                <h2>Formato de archivo no válido</h2>
                <p>Solo se pueden subir archivos .mp4 o .mkv</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;

        case 'Max numero archivos':
            htmlError = `
            <div class="mensajeError">
                <h2>Número máximo de vídeos alcanzado</h2>
                <p>Solo se puede subir un vídeo</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;

        case 'Error al enviar al servidor':
            htmlError = `
            <div class="mensajeError">
                <h2>Error al enviar al servidor</h2>
                <p>Inténtalo de nuevo más tarde</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;

        case 'Error al procesar el video':
            htmlError = `
            <div class="mensajeError">
                <h2>Error al procesar el vídeo</h2>
                <p>Ha ocurrido un error al procesar el vídeo</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;

        case 'Error al crear el vídeo':
            htmlError = `
            <div class="mensajeError">
                <h2>Error al crear el vídeo</h2>
                <p>Ha ocurrido un error al crear el vídeo</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;

        case 'Video vacio':
            htmlError = `
            <div class="mensajeError">
                <h2>No hay vídeo</h2>
                <p>No aparecen las acciones seleccionadas en el vídeo</p>
                <div class="progressBar"><div class="progress"></div></div>
            </div>`;
            break;
    }

    const html = document.getElementById(idZona).innerHTML;
    document.getElementById(idZona).innerHTML = html + htmlError;
    
    // Establece un temporizador para iniciar las barras de progreso después de un pequeño retraso
    setTimeout(function() {
        const progressBars = document.querySelectorAll('.progress');
        for (let i = 0; i < progressBars.length; i++) {
            progressBars[i].style.width = '100%';
        }
    }, 100);
    
    // Establece un temporizador para eliminar el HTML después de 2 segundos
    setTimeout(function() {
        document.querySelector('.mensajeError').remove();
    }, 2000);
}

// -------------------------- FUNCIONES ENVIAR ARCHIVO --------------------------

btnEnviarVideos.onclick = (e) => {
    enviarVideosAlServidor(ficheroAEnviar);
}

async function enviarVideosAlServidor(ficheroAEnviar){
    const formData = new FormData();
    formData.append('video', ficheroAEnviar);

    try{
        
        cargando.classList.remove('oculto');

        let respuesta = await fetch(flaskServerUrl+'/subir_video', {
            method: 'POST',
            body: formData
        });

        if (respuesta.ok){
            respuesta = await respuesta.json();
            cargando.classList.add('oculto');

            console.log('Archivo subido correctamente')

            // Modifica el display de .seccionAcciones por flex
            seccionAcciones.style.display = 'flex';
    
            // Procesa el video
            procesarVideo(respuesta.ruta_video);        
        }
    
    }catch(error){
        console.log(error);
        cargando.classList.add('oculto');
        muestraError('Error al enviar al servidor', 'errorzoneArchivo');
    }
}

// -------------------------- SECCION ACCIONES --------------------------

async function procesarVideo(ruta_video){

    let formData = new FormData();
    formData.append('ruta_video', ruta_video);

    // Desplaza la ventana a seccionAcciones
    seccionAcciones.scrollIntoView({ behavior: 'smooth' });

    // Inicia la actualización del texto de progreso
    actualizarTextoProgreso();

    // Deshabilita el botón al inicio de la animación
    btnElegirAcciones.disabled = true;

    barraProgresoVideos.style.backgroundColor = 'green';
    barraProgresoVideos.style.animationName = 'aumentarAncho';
    barraProgresoVideos.style.animationDuration = '180s';
    barraProgresoVideos.style.animationPlayState = 'running';
    
    try{
        let respuesta = await fetch(flaskServerUrl+'/procesar_video', {
            method: 'POST',
            body: formData
        });

        if (respuesta.ok){
            respuesta = await respuesta.json();

            if (respuesta.error != null){
                console.log('Error al procesar el video');

                // Vuelve a la seccion de subir archivo
                seccionAcciones.style.display = 'none';

                // Muestra un mensaje de error
                muestraError('Error al procesar el video', 'errorzoneArchivo');
                console.log(respuesta.error)
            }else{
                ruta_video_servidor = ruta_video;
                ruta_json = respuesta.ruta_json;

                barraProgresoVideos.style.animationName = 'aumentarAnchoFinal';
                barraProgresoVideos.style.animationDuration = '1s';

                // Añade un evento de finalización de animación a barraProgresoVideos
                barraProgresoVideos.addEventListener('animationend', function() {
                    // Habilita el botón cuando la animación ha terminado
                    btnElegirAcciones.disabled = false;
                });
            }
        }

    }catch(error){
        console.log('Error al procesar el video');

        // Vuelve a la seccion de subir archivo
        seccionAcciones.style.display = 'none';

        // Muestra un mensaje de error
        muestraError('Error al procesar el video', 'errorzoneArchivo');
        console.log(error);

    }
}

// Función para actualizar el texto de progreso
function actualizarTextoProgreso() {
    // Obtiene el ancho de barraProgresoVideos y su contenedor
    const anchoBarra = barraProgresoVideos.getBoundingClientRect().width;
    const anchoContenedor = barraProgresoVideos.parentNode.getBoundingClientRect().width;

    // Calcula el porcentaje
    const porcentaje = (anchoBarra / anchoContenedor) * 100;

    // Redondea el porcentaje hacia abajo a un número entero
    const porcentajeEntero = Math.floor(porcentaje);

    // Establece el texto de textoProgreso en el porcentaje
    textoProgreso.textContent = porcentajeEntero + '%';

    // Solicita el próximo frame de la animación
    requestAnimationFrame(actualizarTextoProgreso);
}

// Añade un event listener a cada elemento para cuando se pulsa las acciones
acciones.forEach(accion => {
    accion.addEventListener('click', () => {
        // Añade la clase 'accionSeleccionada' al elemento clickeado
        accion.classList.toggle('accionSeleccionada');

    });
});

// Hace una solicutud al servidor para obtener el video con las acciones seleccionadas
btnElegirAcciones.addEventListener('click', async function() {
    // Selecciona todos los elementos con la clase accionSeleccionada
    const elementosSeleccionados = document.querySelectorAll('.accionSeleccionada');

    let accionesSeleccionadas = [];

    // Itera sobre los elementos seleccionados
    elementosSeleccionados.forEach(function(elemento) {
        // Selecciona el elemento p dentro del elemento actual
        const p = elemento.querySelector('p');

        // Registra el texto del elemento p
        accionesSeleccionadas.push(p.textContent);
    });

    console.log(accionesSeleccionadas);
    console.log(ruta_video_servidor);
    console.log(ruta_json);

    let formData = new FormData();
    formData.append('acciones_seleccionadas', accionesSeleccionadas);
    formData.append('ruta_video', ruta_video_servidor);
    formData.append('ruta_json', ruta_json);

    // Inicia la actualización del texto de progreso
    actualizarTextoProgreso();

    // Inicia la animación de la barra de progreso
    barraProgresoVideos.style.backgroundColor = 'lightgreen';
    barraProgresoVideos.style.animationName = 'aumentarAncho';
    barraProgresoVideos.style.animationDuration = '60s';
    barraProgresoVideos.style.animationPlayState = 'running';

    try{

        // Envia las acciones seleccionadas al servidor
        let respuesta = await fetch(flaskServerUrl+'/obtener_video_highlights', {
            method: 'POST',
            body: formData
        });

        if (respuesta.ok){

            let contentType = respuesta.headers.get("content-type");

            // Mira si la respuesta es un json o es un archivo adjunto
            if (contentType && contentType.includes("application/json")) {
                respuesta = await respuesta.json();
                if (respuesta.vacio != null) {
                    console.log('Error al procesar el video');
                    muestraError('Video vacio', 'errorzoneAcciones');
                }
            } else {
                // Código para manejar la respuesta que no es vacía (archivo adjunto)
                const blob = await respuesta.blob();
        
                // Crea un enlace temporal para descargar el archivo
                const linkDescarga = document.createElement('a');
                linkDescarga.href = window.URL.createObjectURL(blob);
        
                // Verifica el tipo MIME del Blob y establece el nombre del archivo de descarga en consecuencia
                if (blob.type === 'video/mp4') {
                    linkDescarga.setAttribute('download', 'highlights.mp4');
                } else if (blob.type === 'video/x-matroska') {
                    linkDescarga.setAttribute('download', 'highlights.mkv');
                }
        
                linkDescarga.click();
        
                // Finaliza la animación de la barra de progreso
                barraProgresoVideos.style.animationName = 'aumentarAnchoFinal';
                barraProgresoVideos.style.animationDuration = '1s';
            }

        }else{
            // Muestra un mensaje de error
            muestraError('Error al crear el vídeo', 'errorzoneAcciones');
        }
    
    }catch(error){
        console.log('Error al enviar las acciones al servidor');

        // Muestra un mensaje de error
        muestraError('Error al crear el vídeo', 'errorzoneAcciones');
    }

});