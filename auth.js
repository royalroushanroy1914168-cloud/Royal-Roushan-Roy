const API = localStorage.getItem("API_URL") || "http://localhost:5000/api";
const msg = t => { const e=document.getElementById("message"); if(e)e.textContent=t; };

document.getElementById("registerForm")?.addEventListener("submit", async e=>{
 e.preventDefault();
 if(document.getElementById("password").value!==document.getElementById("confirm").value){msg("Passwords do not match");return;}
 const r=await fetch(API+"/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:name.value,email:email.value,password:password.value})});
 const d=await r.json(); msg(d.error||d.message); if(r.ok)setTimeout(()=>location.href="login.html",700);
});

document.getElementById("loginForm")?.addEventListener("submit", async e=>{
 e.preventDefault(); const r=await fetch(API+"/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:email.value,password:password.value})});
 const d=await r.json(); if(!r.ok){msg(d.error);return;} localStorage.setItem("citizenToken",d.token);localStorage.setItem("citizen",JSON.stringify(d.user));location.href="report.html";
});

document.getElementById("departmentLoginForm")?.addEventListener("submit", async e=>{
 e.preventDefault(); const r=await fetch(API+"/department/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:email.value,password:password.value})});
 const d=await r.json(); if(!r.ok){msg(d.error);return;} localStorage.setItem("departmentToken",d.token);location.href="department-dashboard.html";
});