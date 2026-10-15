(()=>{'use strict';
const $=id=>document.getElementById(id),stage=$('kinetic-stage'),canvas=$('nano-canvas'),toggle=$('motion-toggle');
let recolor=()=>{};
if(stage&&canvas){let gl;try{gl=canvas.getContext('webgl',{antialias:true,alpha:true,powerPreference:'low-power'})}catch(e){}
const fallback=()=>{canvas.style.display='none';const el=$('stage-fallback');if(el)el.style.display='block';if(toggle)toggle.hidden=true;};
if(!gl)fallback();else try{
const vert='attribute vec3 pos;attribute vec3 nrm;uniform float yaw,pitch,aspect;varying vec3 vn;varying vec3 vp;void main(){float cy=cos(yaw),sy=sin(yaw),cx=cos(pitch),sx=sin(pitch);vec3 p=vec3(pos.x*cy+pos.z*sy,pos.y,-pos.x*sy+pos.z*cy);p=vec3(p.x,p.y*cx-p.z*sx,p.y*sx+p.z*cx);vec3 n=vec3(nrm.x*cy+nrm.z*sy,nrm.y,-nrm.x*sy+nrm.z*cy);n=vec3(n.x,n.y*cx-n.z*sx,n.y*sx+n.z*cx);vn=normalize(n);vp=p;float z=4.7-p.z;gl_Position=vec4(p.x*2.25/aspect,p.y*2.25,z,z);}';
const frag='precision mediump float;varying vec3 vn;varying vec3 vp;uniform float mode;void main(){vec3 n=normalize(vn);vec3 l=normalize(vec3(-.4,.8,1.5));float diffuse=max(dot(n,l),0.);float spec=pow(max(dot(reflect(-l,n),normalize(vec3(-vp.x,-vp.y,4.-vp.z))),0.),30.);float fres=pow(1.-max(dot(n,normalize(vec3(-vp.x,-vp.y,4.-vp.z))),0.),2.);vec3 c=mix(vec3(.15,.45,.55),vec3(.76,.99,.60),.55+.3*sin(vp.x*5.+vp.y*3.));if(mode>.5&&mode<1.5)c=mix(c,vec3(1.,.31,.48),.7);if(mode>1.5)c=mix(c,vec3(1.,.80,.47),.7);c=c*(.21+diffuse*.75)+spec*.85+fres*c*.65;gl_FragColor=vec4(c,1.);}';
function compile(type,src){const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(sh));return sh;}
const prog=gl.createProgram();gl.attachShader(prog,compile(gl.VERTEX_SHADER,vert));gl.attachShader(prog,compile(gl.FRAGMENT_SHADER,frag));gl.linkProgram(prog);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(prog));gl.useProgram(prog);
const verts=[],N=120,M=22;
function vertex(u,v,ring){let r=.22+.012*Math.sin(u*22.+v*7.),R=1.0;let x=(R+r*Math.cos(v))*Math.cos(u),y=r*Math.sin(v),z=(R+r*Math.cos(v))*Math.sin(u);let nx=Math.cos(v)*Math.cos(u),ny=Math.sin(v),nz=Math.cos(v)*Math.sin(u);
if(ring===1){let q=y;y=z;z=q;q=ny;ny=nz;nz=q;}if(ring===2){let q=x;x=y;y=q;q=nx;nx=ny;ny=q;}verts.push(x,y,z,nx,ny,nz);}
for(let k=0;k<3;k++)for(let i=0;i<N;i++)for(let j=0;j<M;j++){let u=i*2*Math.PI/N,U=(i+1)*2*Math.PI/N,v=j*2*Math.PI/M,V=(j+1)*2*Math.PI/M;vertex(u,v,k);vertex(U,v,k);vertex(U,V,k);vertex(u,v,k);vertex(U,V,k);vertex(u,V,k);}
const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(verts),gl.STATIC_DRAW);
for(const [name,off] of [['pos',0],['nrm',12]]){const loc=gl.getAttribLocation(prog,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,24,off);}
const U={yaw:gl.getUniformLocation(prog,'yaw'),pitch:gl.getUniformLocation(prog,'pitch'),aspect:gl.getUniformLocation(prog,'aspect'),mode:gl.getUniformLocation(prog,'mode')};
gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);
let reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches,paused=reduced||!!navigator.connection?.saveData,visible=true,frame=0,last=0,yaw=.35,pitch=.35,mode=0,drag=false,px=0,py=0;
const sync=()=>{if(toggle){toggle.textContent=paused?'▶ Animation':'Ⅱ Pause';toggle.setAttribute('aria-pressed',String(paused))}};sync();
function paint(t){frame=0;if(!visible||document.hidden)return;if(!paused&&t-last<36){frame=requestAnimationFrame(paint);return;}last=t;if(!paused)yaw+=.004;
const rect=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.5),w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));
if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}
gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
gl.uniform1f(U.yaw,yaw);gl.uniform1f(U.pitch,pitch);gl.uniform1f(U.aspect,w/h);gl.uniform1f(U.mode,mode);gl.drawArrays(gl.TRIANGLES,0,verts.length/6);
if(!paused)frame=requestAnimationFrame(paint);}
const refresh=()=>{if(!frame&&visible&&!document.hidden)frame=requestAnimationFrame(paint)};
recolor=x=>{mode=x;refresh()};toggle?.addEventListener('click',()=>{paused=!paused;sync();refresh()});
stage.addEventListener('pointerdown',e=>{if(e.target===toggle||!e.isPrimary)return;drag=true;px=e.clientX;py=e.clientY;stage.setPointerCapture(e.pointerId)});
stage.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-px)*.007;pitch=Math.max(-1.3,Math.min(1.3,pitch+(e.clientY-py)*.006));px=e.clientX;py=e.clientY;refresh()});
stage.addEventListener('pointerup',()=>drag=false);stage.addEventListener('pointercancel',()=>drag=false);
stage.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.16;if(e.key==='ArrowRight')yaw+=.16;if(e.key==='ArrowUp')pitch-=.16;if(e.key==='ArrowDown')pitch+=.16;refresh()});
window.addEventListener('resize',refresh,{passive:true});document.addEventListener('visibilitychange',refresh);
if('IntersectionObserver'in window){const io=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)refresh();else if(frame){cancelAnimationFrame(frame);frame=0;}},{threshold:.01});io.observe(stage);}
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fallback()},{once:true});refresh();
}catch(e){console.warn('3D fallback',e);fallback();}}
const demos={verified:{status:'VERIFIED / DEMO',quote:'Die Aktion ist im Zielsystem nachvollziehbar.',record:'Issue-ID und Titel/Status-Abgleich',finding:'Echte Prüfung erfordert unabhängiges Readback.',mode:0},reject:{status:'REJECTED / DEMO',quote:'Der Agent meldet Erfolg. Im Zielsystem fehlt der Eintrag.',record:'Kein passender Datensatz',finding:'Ohne Beleg kein nachgewiesener Erfolg.',mode:1},unknown:{status:'UNKNOWN / DEMO',quote:'Das Zielsystem antwortet nicht. Der Erfolg bleibt unbekannt.',record:'API nicht erreichbar',finding:'Fail-closed: Unbekannt ist nicht erfolgreich.',mode:2}};
document.querySelectorAll('[data-proof]').forEach(btn=>btn.addEventListener('click',()=>{const d=demos[btn.dataset.proof];if(!d)return;document.querySelectorAll('[data-proof]').forEach(x=>x.setAttribute('aria-pressed',String(x===btn)));const box=$('terminal');if(box){box.dataset.kind=btn.dataset.proof;$('proof-status').textContent=d.status;$('proof-quote').textContent=d.quote;$('proof-record').textContent=d.record;$('proof-finding').textContent=d.finding;}recolor(d.mode);}));
const form=$('audit-form');if(form){
const data={missing:{name:'Fehlender Ergebnisnachweis',title:'Den Zielsystem-Nachweis definieren',steps:['Legen Sie vor jeder Aktion fest, welches Zielsystem den Erfolg belegen kann.','Vergleichen Sie nach der Aktion die gespeicherten Daten mit dem erwarteten Ergebnis.','Kennzeichnen Sie fehlende Belege als UNVERIFIED statt erledigt.']},handoff:{name:'Unklare Übergaben',title:'Verantwortung an Übergaben klären',steps:['Notieren Sie Eingang, zuständige Person und Übergabezeit.','Bestimmen Sie ein überprüfbares Kriterium für den Abschluss.','Testen Sie die neue Regel an drei Vorgängen.']},duplicate:{name:'Doppelte Dateneingaben',title:'Eine führende Datenquelle bestimmen',steps:['Markieren Sie jede doppelte Eingabe.','Benennen Sie die maßgebliche Datenquelle.','Prüfen Sie die Übernahme an die nächste Stelle.']},delay:{name:'Wartezeiten und Rückstände',title:'Wartezeit sichtbar machen',steps:['Dokumentieren Sie Eingang und Antwort für fünf Fälle.','Vereinbaren Sie eine verantwortliche Stelle und Frist.','Kontrollieren Sie nach einer Woche die offenen Fälle.']}};
const extra={agents:'Agentenaktionen benötigen einen getrennten lesenden Nachweis.',requests:'Anfragen brauchen einen verständlichen Bearbeitungsstatus.',data:'Keine sensiblen Daten hier eingeben.',appointments:'Übergabe und Abschluss müssen eindeutig erkennbar sein.'};
form.addEventListener('submit',e=>{e.preventDefault();const use=$('usecase').value,pain=$('bottleneck').value,freq=$('volume').value,goal=$('objective').value,o=data[pain],period=freq==='daily'?'täglich':freq==='weekly'?'wöchentlich':'gelegentlich';
$('result').hidden=false;$('result-label').textContent='ERSTBEWERTUNG / '+period.toUpperCase();$('result-title').textContent=o.title;$('result-desc').textContent=extra[use]+' Wiederholung: '+period+'. Regelbasierte Orientierung; keine Zertifizierung oder garantierte Ersparnis.';
const list=$('result-list');list.replaceChildren();o.steps.forEach(s=>{const li=document.createElement('li');li.textContent=s;list.appendChild(li)});
const body='Guten Tag,\n\nich interessiere mich unverbindlich für den CERBERRUS144 Büroablauf-Check.\nBereich: '+use+'\nProblem: '+o.name+'\nHäufigkeit: '+period+'\nZiel: '+goal+'\n\nBitte vorab Umfang, Termin und Voraussetzungen bestätigen.';
$('result-contact').href='mailto:cerberrus144-os@agentmail.to?subject='+encodeURIComponent('Inbound CERBERRUS144 | Büroablauf-Check')+'&body='+encodeURIComponent(body);
$('result').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'nearest'});});}
})();