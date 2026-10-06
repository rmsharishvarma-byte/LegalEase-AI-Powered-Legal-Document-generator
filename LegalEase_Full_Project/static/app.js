const state={key:"rental",title:"Rental Agreement",content:""};
const titles={rental:"Rental Agreement",nda:"Non-Disclosure Agreement",employment:"Employment Contract",freelance:"Freelance Service Agreement"};

const date=document.getElementById("date");
date.value=new Date().toISOString().slice(0,10);
setPaperDate();

document.querySelectorAll(".type").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".type").forEach(x=>x.classList.remove("active"));
    btn.classList.add("active");
    state.key=btn.dataset.key;
    state.title=titles[state.key];
    setTitles();
  });
});

function setTitles(){
  document.getElementById("title").textContent=state.title;
  document.getElementById("paperTitle").textContent=state.title;
}
function setPaperDate(){
  document.getElementById("paperDate").textContent=new Date().toLocaleDateString("en-IN",{day:"2-digit",month:"long",year:"numeric"});
}

document.querySelectorAll(".chips button").forEach(btn=>{
  btn.addEventListener("click",()=>{
    const field=document.getElementById("requirements");
    field.value+=(field.value?"\n":"")+btn.dataset.add;
    field.focus();
  });
});

document.getElementById("generate").addEventListener("click",async()=>{
  const btn=document.getElementById("generate");
  const text=document.getElementById("generateText");
  btn.disabled=true;text.textContent="AI is drafting…";

  const payload={
    document_type:state.key,
    party_a:document.getElementById("partyA").value,
    party_b:document.getElementById("partyB").value,
    date:date.value,
    amount:document.getElementById("amount").value,
    duration:document.getElementById("duration").value,
    jurisdiction:document.getElementById("jurisdiction").value,
    requirements:document.getElementById("requirements").value
  };

  try{
    const res=await fetch("/api/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await res.json();
    if(!res.ok) throw new Error(data.detail||"Generation failed");
    state.title=data.title;state.content=data.content;setTitles();
    renderDocument(data.content);
    addMessage("ai","Draft ready. I created a structured first version from your inputs. You can ask me about a clause or update the requirements and regenerate.");
  }catch(err){
    addMessage("ai","I couldn't generate the draft: "+err.message);
  }finally{
    btn.disabled=false;text.textContent="Generate with AI";
  }
});

function renderDocument(text){
  const content=document.getElementById("content");
  content.innerHTML="";
  text.split(/\n\s*\n/).forEach(block=>{
    const lines=block.trim().split("\n");
    if(!lines[0])return;
    const h=lines[0].match(/^\d+\.\s+(.+)/);
    if(h){
      const el=document.createElement("h3");el.textContent=lines[0];content.appendChild(el);
      if(lines.slice(1).join(" ").trim()){
        const p=document.createElement("p");p.textContent=lines.slice(1).join(" ");content.appendChild(p);
      }
    }else{
      const p=document.createElement("p");p.textContent=block;content.appendChild(p);
    }
  });
  setPaperDate();
}

function addMessage(who,text){
  const chat=document.getElementById("chat");
  const row=document.createElement("div");row.className="msg "+who;
  row.innerHTML=who==="ai"?`<i>✦</i><div>${escapeHtml(text)}</div>`:`<div>${escapeHtml(text)}</div>`;
  chat.appendChild(row);chat.scrollTop=chat.scrollHeight;
}

async function sendChat(){
  const input=document.getElementById("chatInput");
  const message=input.value.trim();if(!message)return;
  addMessage("user",message);input.value="";
  try{
    const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message,document_type:state.title,current_document:state.content})});
    const data=await res.json();
    addMessage("ai",data.reply||"Please update the requirements and regenerate.");
  }catch{
    addMessage("ai","The AI chat service is unavailable right now. You can still update the requirements and regenerate the draft.");
  }
}
document.getElementById("send").addEventListener("click",sendChat);
document.getElementById("chatInput").addEventListener("keydown",e=>{if(e.key==="Enter")sendChat()});

document.getElementById("copy").addEventListener("click",async()=>{
  await navigator.clipboard.writeText(document.getElementById("content").innerText);
  const b=document.getElementById("copy");b.textContent="Copied ✓";setTimeout(()=>b.textContent="Copy",1200);
});

document.getElementById("pdf").addEventListener("click",async()=>{
  if(!state.content){alert("Generate a document first.");return;}
  const b=document.getElementById("pdf");b.textContent="Exporting…";b.disabled=true;
  try{
    const res=await fetch("/api/pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title:state.title,content:state.content})});
    if(!res.ok)throw new Error("PDF export failed");
    const blob=await res.blob(),url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download=state.title.replaceAll(" ","_")+".pdf";a.click();URL.revokeObjectURL(url);
  }catch(e){alert(e.message)}
  finally{b.textContent="Export PDF";b.disabled=false}
});

document.getElementById("themeBtn").addEventListener("click",()=>document.body.classList.toggle("light"));
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
