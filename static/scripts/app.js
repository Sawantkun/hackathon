// dark theme 
const theme=document.querySelector('.logo');
theme.addEventListener('click',()=>{
  document.body.classList.toggle('dark-theme');
  console.log('theme clicked')
})

const menu = document.querySelector('#menu');
const hidden = document.querySelector('.hidden');
menu.addEventListener('click',()=>{
    hidden.classList.toggle('ham');
})

let fileInput = document.getElementById('file-input');
let imageContainer = document.getElementById('images');
let numofFiles = document.getElementById('nofiles');
const container = document.querySelector('.container');
const submit = document.querySelector('input[type="submit"]');

function preview(){ 
  container.style.width = '60%';
  container.style.height = '60%';
  submit.style.display = 'block';
  imageContainer.innerHTML = '';
  numofFiles.textContent = `${fileInput.files.length} Files Selected`;

  for(i of fileInput.files){
    let reader = new FileReader();
    let figure = document.createElement('figure');
    let figCap = document.createElement('figcaption');
    figCap.innerText = i.name;
    figure.appendChild(figCap);
    reader.onload=()=>{
        let img =document.createElement('img');
        img.setAttribute('src',reader.result);
        figure.insertBefore(img, figCap);
    }
    imageContainer.appendChild(figure);
    reader.readAsDataURL(i);
  }
};


// Select your input type file and store it in a variable
const input = document.getElementById("file-input");

// This will upload the file after having read it
const upload = (file) => {
  fetch("/classify_upload", {
    // Your POST endpoint
    method: "POST",
    headers: {
      // Content-Type may need to be completely *omitted*
      // or you may need something
      "Content-Type":
        "multipart/form-data; boundary=—-WebKitFormBoundaryfgtsKTYLsT7PNUVD",
    },
    body: file, // This is your file object
  })
    .then(
      (response) => response.json() // if the response is a JSON object
    )
    .then(
      (success) => console.log(success) // Handle the success response object
    )
    .catch(
      (error) => console.log(error) // Handle the error response object
    );
};

// Event handler executed when a file is selected
const onSelectFile = () => upload(input.files[0]);

// Add a listener on your input
// It will be triggered when a file will be selected

input.addEventListener("change", onSelectFile, false)