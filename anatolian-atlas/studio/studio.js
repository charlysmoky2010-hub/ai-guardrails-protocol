(() => {
  "use strict";

  const canvas = document.getElementById("marbling");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d", { alpha: false });
  if (!ctx) return;
  const W = canvas.width, H = canvas.height;
  const MAX_DROPS = 48;
  const STEP_POINTS = 80;
  const palettes = {
    iznik: ["#123b65", "#237b96", "#d59a4b", "#b94e48", "#d9c398", "#4c7890"],
    rose: ["#a43d61", "#ce7167", "#d7a568", "#657d62", "#e6c5aa", "#6d4962"],
    nocturne: ["#182e51", "#5c5980", "#d6b678", "#6b9896", "#a66d71", "#394e72"]
  };
  const labels = {
    en: {
      langLabel:"Language",browse:"Explore collection ↗",introTag:"A LITTLE WATER, A WORLD OF COLOUR",hero:"Let the water <em>lead.</em>",
      intro:"Discover the joy of colour in motion. Place drops, drag a comb through the water, and make a pattern that is entirely yours.",
      free:"FREE CREATIVE PLAY",private:"NO ACCOUNT · NO UPLOADS",workshop:"INTERACTIVE WORKSHOP / NO. 01",workbenchTitle:"Your digital water",
      workbenchHint:"Tap to add a colour drop. Switch to the comb and drag to transform the surface.",
      paperTop:"ANATOLIAN ATLAS / EXPERIMENTAL PATTERN",paperBottom:"DIGITAL STUDY • NOT PHYSICAL EBRU",
      toolkit:"THE ARTIST'S TRAY",tool:"CHOOSE A TOOL",drop:"Drop",comb:"Comb",palette:"COLOUR STORY",
      iznik:"İznik blue",rose:"Rose garden",nocturne:"Night current",size:"DROP SIZE",
      new:"✦ New composition",clear:"Clear the water",download:"Download your PNG",savePinterest:"Save this studio on Pinterest ↗",
      status:"Try a drop. Every composition starts somewhere.",shortcut:"Keyboard: focus the water, move with arrow keys, and press Enter or Space to add a drop.",
      originTitle:"An old art form.<br><em>An endless beginning.</em>",
      origin:"Turkish Ebru is an art of pigments floated on specially prepared water and transferred to paper. This browser toy is an original digital interpretation of colour and movement — not the physical craft or a replacement for a handmade Ebru artwork.",
      premiumTag:"FOR THE WALL / FOR THE HEART",premiumTitle:"Love the feeling?<br><em>Meet the art.</em>",
      premiumBody:"Explore Anatolian Atlas Ebru Studies Vol. 1: six digital art reproductions, printable JPGs, a collection guide and a personal-use licence. A curated collection, distinct from this free pattern maker.",
      price:"€18+ · ONE-TIME DIGITAL COLLECTION",offerCta:"Explore Ebru Studies Vol. 1 ↗",
      disclaimer:"Checkout, price, taxes and delivery are determined by Ko-fi. Please confirm the listing before paying. This free studio does not process payments.",
      footer:"Art has no borders. Water remembers.",privacyFooter:"CREATED IN YOUR BROWSER · NO LOGIN · NO TRACKING",
      drops:"DROPS",placed:"A new colour has entered the water.",combed:"The colours are moving.",cleared:"The water is clear. Make your first drop.",
      newMade:"A new pattern is ready for you.",saved:"Your digital pattern was prepared as a PNG.",keyboard:"Keyboard cursor moved."
    },
    de: {
      langLabel:"Sprache",browse:"Kollektion entdecken ↗",introTag:"EIN WENIG WASSER, EINE WELT VOLLER FARBE",hero:"Lass das Wasser <em>führen.</em>",
      intro:"Entdecke Farbe in Bewegung. Setze Tropfen, ziehe einen Kamm durchs Wasser und gestalte dein ganz eigenes Muster.",
      free:"KOSTENLOSES KREATIVSPIEL",private:"OHNE KONTO · OHNE UPLOADS",workshop:"INTERAKTIVES STUDIO / NR. 01",workbenchTitle:"Dein digitales Wasser",
      workbenchHint:"Tippe, um einen Farbtropfen zu setzen. Wechsle zum Kamm und ziehe ihn über die Fläche.",
      paperTop:"ANATOLIAN ATLAS / EXPERIMENTELLES MUSTER",paperBottom:"DIGITALE STUDIE • KEIN PHYSISCHES EBRU",
      toolkit:"DIE FARBWERKSTATT",tool:"WERKZEUG WÄHLEN",drop:"Tropfen",comb:"Kamm",palette:"FARBWELT",
      iznik:"İznik-Blau",rose:"Rosengarten",nocturne:"Nachtströmung",size:"TROPFENGRÖSSE",
      new:"✦ Neues Muster",clear:"Wasser leeren",download:"PNG herunterladen",savePinterest:"Dieses Studio auf Pinterest speichern ↗",
      status:"Probiere einen Tropfen. Jedes Muster beginnt irgendwo.",shortcut:"Tastatur: Wasser fokussieren, mit Pfeiltasten bewegen und mit Enter oder Leertaste einen Tropfen setzen.",
      originTitle:"Eine alte Kunstform.<br><em>Ein neuer Anfang.</em>",
      origin:"Türkisches Ebru entsteht, indem Pigmente auf speziell vorbereitetem Wasser schwimmen und auf Papier übertragen werden. Dieses Browser-Spiel ist eine freie digitale Interpretation von Farbe und Bewegung, keine Simulation des echten Handwerks.",
      premiumTag:"FÜR DIE WAND / FÜRS HERZ",premiumTitle:"Du magst das Gefühl?<br><em>Entdecke die Kunst.</em>",
      premiumBody:"Entdecke Anatolian Atlas Ebru Studies Vol. 1: sechs digitale Kunstreproduktionen, druckbare JPGs, einen Kollektionsführer und eine Lizenz für den Privatgebrauch. Echte kuratierte Arbeiten, unabhängig von diesem kostenlosen Musterwerkzeug.",
      price:"AB 18 € · EINMALIGE DIGITALKOLLEKTION",offerCta:"Ebru Studies Vol. 1 ansehen ↗",
      disclaimer:"Bestellprozess, Preis, Steuern und Lieferung bestimmt Ko-fi. Bitte vor dem Kauf das Angebot prüfen. Dieses Gratis-Studio verarbeitet keine Zahlungen.",
      footer:"Kunst kennt keine Grenzen. Wasser erinnert sich.",privacyFooter:"IM BROWSER ERSTELLT · KEIN LOGIN · KEIN TRACKING",
      drops:"TROPFEN",placed:"Ein neuer Farbtropfen fließt ins Wasser.",combed:"Die Farben bewegen sich.",cleared:"Das Wasser ist leer. Setze den ersten Tropfen.",
      newMade:"Ein neues Muster ist bereit.",saved:"Dein digitales Muster wurde als PNG vorbereitet.",keyboard:"Tastaturcursor bewegt."
    },
    tr: {
      langLabel:"Dil",browse:"Koleksiyonu keşfet ↗",introTag:"BİR DAMLA SU, BİNLERCE RENK",hero:"Bırak, su <em>anlatsın.</em>",
      intro:"Hareket eden renklerin neşesini keşfet. Damla bırak, tarağı suyun üzerinde gezdir ve tamamen sana ait bir desen yarat.",
      free:"ÜCRETSİZ YARATICI DENEYİM",private:"HESAP YOK · YÜKLEME YOK",workshop:"ETKİLEŞİMLİ ATÖLYE / NO. 01",workbenchTitle:"Senin dijital suyun",
      workbenchHint:"Renk damlatmak için dokun. Tarak aracına geçip sürükleyerek desenleri dönüştür.",
      paperTop:"ANATOLIAN ATLAS / DENEYSEL DESEN",paperBottom:"DİJİTAL ÇALIŞMA • GERÇEK EBRU DEĞİLDİR",
      toolkit:"SANATÇININ RENK TEPSİSİ",tool:"ARACI SEÇ",drop:"Damla",comb:"Tarak",palette:"RENK HİKÂYESİ",
      iznik:"İznik mavisi",rose:"Gül bahçesi",nocturne:"Gece akıntısı",size:"DAMLA BOYUTU",
      new:"✦ Yeni kompozisyon",clear:"Suyu temizle",download:"PNG olarak indir",savePinterest:"Bu stüdyoyu Pinterest'te kaydet ↗",
      status:"Bir damla dene. Her kompozisyon bir yerden başlar.",shortcut:"Klavye: tuvali seç, oklarla hareket et; Enter veya Boşluk ile damla bırak.",
      originTitle:"Kadim bir sanat.<br><em>Sonsuz bir başlangıç.</em>",
      origin:"Türk ebrusu, özel olarak hazırlanmış su yüzeyinde yüzdürülen boyaların kâğıda aktarılması sanatıdır. Bu tarayıcı deneyimi renk ve hareketten esinlenen özgün bir dijital yorumdur; gerçek ebru yapımının veya el emeği bir eserin yerine geçmez.",
      premiumTag:"DUVAR İÇİN / KALP İÇİN",premiumTitle:"Bu hissi sevdin mi?<br><em>Sanatı tanı.</em>",
      premiumBody:"Anatolian Atlas Ebru Studies Vol. 1 koleksiyonunu keşfet: altı dijital sanat reprodüksiyonu, baskıya uygun JPG'ler, koleksiyon rehberi ve kişisel kullanım lisansı. Bu ücretsiz desen aracından farklı, özenle seçilmiş sanat eserleri.",
      price:"18 €+ · TEK SEFERLİK DİJİTAL KOLEKSİYON",offerCta:"Ebru Studies Vol. 1'i keşfet ↗",
      disclaimer:"Ödeme, güncel fiyat, vergiler ve teslimat Ko-fi tarafından belirlenir. Satın almadan önce ilanı doğrula. Bu ücretsiz stüdyo ödeme almaz.",
      footer:"Sanatın sınırı yoktur. Su hatırlar.",privacyFooter:"TARAYICINDA ÜRETİLİR · ÜYELİK YOK · İZLEME YOK",
      drops:"DAMLA",placed:"Suya yeni bir renk damladı.",combed:"Renkler hareket ediyor.",cleared:"Su temizlendi. İlk damlanı bırak.",
      newMade:"Yeni bir desen hazır.",saved:"Dijital desenin PNG olarak hazırlandı.",keyboard:"Klavye imleci hareket etti."
    }
  };

  const $ = (id) => document.getElementById(id);
  const status = $("studio-status");
  const count = $("drop-count");
  const toolDrop = $("tool-drop");
  const toolComb = $("tool-comb");
  const sizeInput = $("drop-size");
  const languageInput = $("language");
  const brushValue = $("drop-size-value");
  let language = "en";
  let tool = "drop";
  let palette = "iznik";
  let rings = [];
  let droplets = 0;
  let colorIndex = 0;
  let seed = 48319;
  let dragging = false;
  let previous = null;
  let keyboardCursor = {x:W/2,y:H/2};

  function rand() {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  }
  function tr(key) { return labels[language][key] || labels.en[key] || key; }
  function say(key) { status.textContent = tr(key); }
  function updateCount() { count.textContent = String(droplets).padStart(2,"0") + " " + tr("drops"); }
  function setLanguage(next) {
    if (!labels[next]) return;
    language = next;
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach(el => {
      el.textContent = tr(el.dataset.i18n);
    });
    // These translations are static, authored markup; no user-supplied HTML.
    document.querySelectorAll("[data-i18n-html]").forEach(el => {
      el.innerHTML = tr(el.dataset.i18nHtml);
    });
    canvas.setAttribute("aria-label", language === "tr"
      ? "Etkileşimli dijital ebru tuvali. Damlatmak için tıkla, tarakla sürükle. Ok tuşlarıyla gez, Enter ile damlat."
      : language === "de"
      ? "Interaktive digitale Marmorierfläche. Für Tropfen klicken, mit dem Kamm ziehen. Pfeiltasten bewegen den Cursor, Enter setzt einen Tropfen."
      : "Interactive digital marbling canvas. Click for a drop or drag with the Comb tool. Arrow keys move the keyboard cursor, Enter adds a drop.");
    updateCount();
  }

  const paper = document.createElement("canvas");
  paper.width=W; paper.height=H;
  const pc=paper.getContext("2d", {alpha:false});
  if (pc) {
    pc.fillStyle="#efe8d7";
    pc.fillRect(0,0,W,H);
    const rng = (() => {
      let value=712331;
      return () => { value=(Math.imul(value,1664525)+1013904223)>>>0; return value/4294967296; };
    })();
    for (let i=0;i<4700;i++){
      const x=rng()*W,y=rng()*H,r=rng()*1.7+.25;
      pc.fillStyle=i%4===0?"rgba(106,83,61,.09)":"rgba(255,255,255,.12)";
      pc.beginPath();pc.arc(x,y,r,0,Math.PI*2);pc.fill();
    }
  }

  function draw() {
    if (pc) ctx.drawImage(paper,0,0);
    else {ctx.fillStyle="#efe8d7";ctx.fillRect(0,0,W,H);}
    for(const ring of rings){
      const points=ring.points;
      if(points.length<3)continue;
      ctx.beginPath();
      ctx.moveTo(points[0].x,points[0].y);
      for(let i=1;i<points.length;i++) ctx.lineTo(points[i].x,points[i].y);
      ctx.closePath();
      ctx.fillStyle=ring.color;ctx.fill();
      ctx.strokeStyle="rgba(24,48,55,.11)";
      ctx.lineWidth=2.3;ctx.stroke();
    }
  }
  function shiftAway(x,y,radius) {
    const scale=radius*2.2;
    for(const ring of rings){
      for(const point of ring.points){
        let dx=point.x-x,dy=point.y-y;
        let length=Math.hypot(dx,dy);
        if(length<.1){dx=.1;dy=.1;length=Math.hypot(dx,dy);}
        const push=.72*radius*Math.exp(-.5*(length/scale)**2);
        point.x+=dx/length*push;
        point.y+=dy/length*push;
      }
    }
  }
  function circle(cx,cy,r,color) {
    const points=[];
    const phase=rand()*Math.PI*2;
    const wobble=rand()*.07+.022;
    for(let i=0;i<STEP_POINTS;i++){
      const a=i*Math.PI*2/STEP_POINTS;
      const ripple=1+wobble*Math.sin(5*a+phase)+.025*Math.sin(11*a-phase);
      points.push({x:cx+Math.cos(a)*r*ripple,y:cy+Math.sin(a)*r*ripple});
    }
    rings.push({color,points});
  }
  function addDrop(x,y,size,paint=true) {
    if (rings.length >= MAX_DROPS*4) rings.splice(0,4);
    shiftAway(x,y,size);
    const colors=palettes[palette];
    const offset=colorIndex++;
    const outer=colors[offset%colors.length];
    const middle=colors[(offset+2)%colors.length];
    const core=colors[(offset+4)%colors.length];
    circle(x,y,size,outer);
    circle(x,y,size*.84,middle);
    circle(x,y,size*.57,core);
    circle(x,y,size*.18,colors[(offset+1)%colors.length]);
    droplets++;
    if(paint){draw();updateCount();say("placed");}
  }
  function combLine(x,y,dx,dy) {
    const influence=Number(sizeInput.value)*2.8;
    const move=Math.min(100,Math.hypot(dx,dy));
    if(move<.1)return;
    const fx=dx*Math.min(1,100/Math.hypot(dx,dy));
    const fy=dy* Math.min(1,100/Math.hypot(dx,dy));
    for(const ring of rings){
      for(const point of ring.points){
        const distance=Math.hypot(point.x-x,point.y-y);
        const weight=Math.exp(-.5*(distance/influence)**2);
        point.x+=fx*weight*.82;
        point.y+=fy*weight*.82;
      }
    }
    draw();
  }
  function setTool(next) {
    tool=next;
    for(const [name,button] of [["drop",toolDrop],["comb",toolComb]]) {
      const isActive=name===next;
      button.classList.toggle("selected",isActive);
      button.setAttribute("aria-pressed",String(isActive));
    }
    canvas.style.cursor=next==="drop"?"crosshair":"grab";
  }
  function setPalette(next) {
    if(!palettes[next]) return;
    palette=next;
    document.querySelectorAll("[data-palette]").forEach(button=>{
      const selected=button.dataset.palette===next;
      button.classList.toggle("selected",selected);
      button.setAttribute("aria-pressed",String(selected));
    });
  }
  function position(event){
    const rect=canvas.getBoundingClientRect();
    const x=(event.clientX-rect.left)*W/rect.width;
    const y=(event.clientY-rect.top)*H/rect.height;
    return {x:Math.max(0,Math.min(W,x)),y:Math.max(0,Math.min(H,y))};
  }
  function newComposition() {
    rings=[];droplets=0;colorIndex=0;
    seed=(Math.floor(Date.now() % 0xffffffff)>>>0)||48319;
    const size=Number(sizeInput.value);
    const picks=7;
    for(let i=0;i<picks;i++) {
      const x=(.15+rand()*.70)*W;
      const y=(.18+rand()*.64)*H;
      addDrop(x,y,size*(.75+rand()*.7),false);
    }
    draw();updateCount();say("newMade");
  }
  canvas.addEventListener("pointerdown", event=>{
    if(event.button!==undefined&&event.button!==0)return;
    event.preventDefault();
    canvas.focus({preventScroll:true});
    const p=position(event);
    keyboardCursor=p;
    if(tool==="drop") {
      addDrop(p.x,p.y,Number(sizeInput.value));
    }else{
      dragging=true;
      previous=p;
      canvas.setPointerCapture?.(event.pointerId);
    }
  });
  canvas.addEventListener("pointermove",event=>{
    if(!dragging||tool!=="comb"||!previous)return;
    event.preventDefault();
    const p=position(event);
    combLine(p.x,p.y,p.x-previous.x,p.y-previous.y);
    previous=p;
    say("combed");
  });
  function stopDrag(){dragging=false;previous=null;}
  canvas.addEventListener("pointerup",stopDrag);
  canvas.addEventListener("pointercancel",stopDrag);
  canvas.addEventListener("lostpointercapture",stopDrag);
  canvas.addEventListener("keydown",event=>{
    const step=event.shiftKey?85:35;
    if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Enter"," "].includes(event.key))event.preventDefault();
    if(event.key==="ArrowLeft")keyboardCursor.x=Math.max(0,keyboardCursor.x-step);
    else if(event.key==="ArrowRight")keyboardCursor.x=Math.min(W,keyboardCursor.x+step);
    else if(event.key==="ArrowUp")keyboardCursor.y=Math.max(0,keyboardCursor.y-step);
    else if(event.key==="ArrowDown")keyboardCursor.y=Math.min(H,keyboardCursor.y+step);
    else if(event.key==="Enter"||event.key===" "){
      addDrop(keyboardCursor.x,keyboardCursor.y,Number(sizeInput.value));
      return;
    }else return;
    say("keyboard");
  });

  $("new-pattern").addEventListener("click",newComposition);
  $("clear-pattern").addEventListener("click",()=>{
    rings=[];droplets=0;draw();updateCount();say("cleared");
  });
  $("download").addEventListener("click",()=>{
    const link=document.createElement("a");
    link.href=canvas.toDataURL("image/png");
    link.download="anatolian-atlas-digital-water-study.png";
    document.body.appendChild(link);
    link.click();link.remove();
    say("saved");
  });
  languageInput.addEventListener("change",()=>setLanguage(languageInput.value));
  toolDrop.addEventListener("click",()=>setTool("drop"));
  toolComb.addEventListener("click",()=>setTool("comb"));
  sizeInput.addEventListener("input",()=>{brushValue.textContent=sizeInput.value;});
  document.querySelectorAll("[data-palette]").forEach(button=>
    button.addEventListener("click",()=>setPalette(button.dataset.palette))
  );
  // Explicit user click only. No Pinterest JS, cookies, trackers or API calls.
  // The image is the existing Anatolian Atlas cover (not a visitor's private PNG).
  const pinterestShareBase = "https://www.pinterest.com/pin/create/button/";
  const pinterestTarget = "https://charlysmoky2010-hub.github.io/ai-guardrails-protocol/anatolian-atlas/studio/?utm_source=pinterest&utm_medium=organic&utm_campaign=aa_water_studio_v1";
  const pinterestMedia = "https://static.metricool.com/planner/202611/7068536-file-2516177163958910896.jpeg";
  const pinterestDescription = "Free digital Ebru-inspired marbling studio: drop colours, comb the water, and download your own PNG design. Explore Anatolian Atlas art and culture.";
  const pinterestHref = pinterestShareBase
    + "?url=" + encodeURIComponent(pinterestTarget)
    + "&media=" + encodeURIComponent(pinterestMedia)
    + "&description=" + encodeURIComponent(pinterestDescription);
  $("pinterest-share").href = pinterestHref;

  newComposition();
  setLanguage("en");
})();
