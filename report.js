const API = localStorage.getItem("API_URL") || "http://localhost:5000/api";
const token = localStorage.getItem("citizenToken");
if(!token) location.href="login.html";

document.getElementById("locate").onclick=()=>{
 if(!navigator.geolocation){alert("Location is not supported by this browser.");return;}
 navigator.geolocation.getCurrentPosition(p=>{latitude.value=p.coords.latitude;longitude.value=p.coords.longitude; if(!location.value)location.value="Current location captured";},()=>alert("Unable to get location. Please allow location access."));
};

document.getElementById("reportForm").onsubmit=async e=>{
 e.preventDefault(); const fd=new FormData();
 ["problem_type","description","location","latitude","longitude","contact"].forEach(id=>fd.append(id,document.getElementById(id).value));
 const file=document.getElementById("image").files[0]; if(file)fd.append("image",file);
 const r=await fetch(API+"/reports",{method:"POST",headers:{Authorization:"Bearer "+token},body:fd});
 const d=await r.json(); if(!r.ok){document.getElementById("message").textContent=d.error;return;}
 localStorage.setItem("lastComplaint",JSON.stringify({...d,problem_type:document.getElementById("problem_type").value}));
 location.href="acknowledgement.html";
};