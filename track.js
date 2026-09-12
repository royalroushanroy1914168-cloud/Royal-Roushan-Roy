const API=localStorage.getItem("API_URL")||"http://localhost:5000/api";
document.getElementById("trackForm").onsubmit=async e=>{
 e.preventDefault();const id=document.getElementById("tracking_id").value.trim();const box=document.getElementById("result");
 const r=await fetch(API+"/reports/track/"+encodeURIComponent(id));const d=await r.json();
 if(!r.ok){box.innerHTML=`<p class="error">${d.error}</p>`;return;}
 box.innerHTML=`<div class="details"><p><b>Tracking ID:</b> ${d.tracking_id}</p><p><b>Problem:</b> ${d.problem_type}</p><p><b>Description:</b> ${d.description}</p><p><b>Location:</b> ${d.location||"-"}</p><p><b>Priority:</b> ${d.priority_score}</p><p><b>Status:</b> <strong>${d.status}</strong></p><p><b>Last Updated:</b> ${new Date(d.updated_at).toLocaleString()}</p></div>`;
};