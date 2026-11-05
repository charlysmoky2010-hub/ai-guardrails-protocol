import {MEDIA,FAMILIES,FILTERS,OFFERS,normalizeLang,normalizeFilter,searchCrafts,listingForCraft,visibleOffers,makeMakerDraft,confirmedSalesFromCatalog} from "./catalog.mjs";

const translations={
 tr:{
 navExplore:"Sanatları keşfet",navWorks:"Eserler",navStudio:"Dijital atölye",navMakers:"Üreticiler için",language:"Dil",
 eyebrow:"BİR SANATIN DEĞİL, BİR KÜLTÜRÜN ATLASI",hero:"Geçmişi<br>koruyan.<br><em>Geleceği</em><br>dokuyan.",
 heroText:"Ebru'dan çiniye, telkâriden minyatüre, kilimden ahşap baskıya. Anadolu'nun yaşayan sanatlarını keşfet; sanatçılarla doğrudan buluşan bir dünyanın temellerine katıl.",
 exploreButton:"Sanatları keşfet",makerButton:"Üretici olarak katıl",heroNote:"Bağımsız kültürel keşif · Doğrulanmamış ürün veya üretici ilanı yok",
 heroArt:"KÜLTÜREL HARİTA / DİJİTAL YORUM",statArts:"SANAT DİSİPLİNİ",statLang:"DİL / TR · EN · DE",
 statOffer:"BAĞLANTISI DOĞRULANMIŞ ÜRÜN",statCaption:"Disiplin sayısı, satışa hazır eser veya onaylı üretici sayısı değildir.",
 exploreKicker:"KÜLTÜREL KEŞİF",exploreTitle:"Sanat bir <em>haritadır.</em>",
 exploreLead:"Geleneksel teknikleri araştır, ilgine göre süz. Her kart bir sanat dalıdır; satış ilanı değildir.",
 searchLabel:"Sanat veya teknik ara",searchPlaceholder:"Örn. dokuma, ebru, telkâri",
 familyLabel:"Malzeme / aile",usageLabel:"Ne için keşfediyorsun?",clear:"Filtreleri temizle ↺",
 allFamilies:"Tüm sanat aileleri",paper:"Kâğıt ve kitap",ceramics:"Çini ve seramik",textile:"Dokuma ve lif",jewelry:"Takı ve telkâri",wood:"Ahşap",metal:"Metal",glass:"Cam",other:"Diğer ustalıklar",
 allUses:"Tüm amaçlar",wall:"Duvar / sanat",home:"Ev / mekân",wear:"Giyilebilir sanat",gift:"Hediye",collect:"Koleksiyon",learn:"Öğrenme",
 count:"sanat dalı bulundu",catalogNotice:"Kültürel dizin • İlan sayısı değildir",none:"Eşleşme bulunamadı",noResults:"Eşleşme bulunamadı.",noResultsBody:"Başka bir sanat adı veya kullanım amacı deneyebilirsin.",
 craftAvailable:"Mevcut ürün bağlantısı",craftPending:"Üretici / eser kaydı bekleniyor",craftOpen:"Eserleri görüntüle",craftDiscover:"Durumu incele",
 worksKicker:"KANITLANMIŞ BAĞLANTI / KÜRASYON",worksTitle:"Eser ile <em>vaadi ayır.</em>",
 worksLead:"Yalnızca mevcut satış bağlantısını bildiğimiz koleksiyonları listeliyoruz. Ödeme, fiyat, vergi ve teslimat koşulları satıcı platformunda teyit edilmelidir.",
 offerTag:"MEVCUT KO-FI LİSTESİ",offerDigital:"DİJİTAL KOLEKSİYON",offerBody:"Altı dijital Ebru sanatı reprodüksiyonu, baskıya uygun dosyalar ve koleksiyon rehberi. Lisans ve teslimat koşullarını Ko-fi'de kontrol et.",
 offerGo:"Ko-fi'de incele ↗",offerUnknown:"Bu seçim için doğrulanmış satış bağlantısı henüz yok.",offerUnknownTitle:"Henüz ürün ilanı bulunmuyor",
 offerDisclaimer:"Satış bağlantısı gerçek; ödeme veya teslimat gerçekleştiği iddia edilmiyor.",
 studioKicker:"DİJİTAL DENEYİM / ÜCRETSİZ",studioTitle:"Suyun içinde<br><em>ilk desenini</em> bırak.",
 studioLead:"Tarayıcında renk damlat, tarağı gezdir ve oluşturduğun deseni PNG olarak indir. Bu, gerçek fiziksel Ebru üretimi değildir.",
 studioAction:"Dijital Ebru atölyesini aç",
 makerKicker:"USTA / SANATÇI / ÜRETİCİ",makerTitle:"Atlasın bir parçası<br><em>sen ol.</em>",
 makerLead:"Üretici ilanının ilk taslağını kendi tarayıcında oluştur. Kaydettiğin JSON sana aittir; henüz bir hesap açılmaz ve hiçbir şey yayımlanmaz.",
 makerName:"Sanatçı / atölye adı *",makerCraft:"Sanat dalı *",makerCity:"Şehir / bölge",
 makerDesc:"Eser ve üretim tekniğini anlat *",makerContact:"İletişim (yalnızca taslak dosyana kaydedilir)",
 saveDraft:"İlan taslağını indir",makerSuccess:"Taslak indirildi. Hiçbir bilgi sunucuya gönderilmedi.",
 makerError:"Lütfen sanatçı adını, sanat dalını ve en az 20 karakterlik açıklamayı kontrol et.",
 makerNoteTitle:"Önce sanat. Sonra güven.",makerNote:"Kendi satışını veya başka üreticilerin eserlerini doğrulamadan ilan etmiyoruz. Platform henüz kamuya açık üretici hesabı, mesajlaşma veya ödeme aracılığı sunmuyor.",
 makerNoteFoot:"İŞLEMLER YALNIZCA TARAYICINDA / SUNUCUYA GÖNDERİM YOK",
 footerManifesto:"Sanatın sınırı yok. Ustalığın hafızası var.",footerDirectory:"DİZİN",footerTrust:"ŞEFFAFLIK",
 footerHonesty:"Üretici sayısı veya satış iddiası oluşturulmaz. Ko-fi harici ödeme alınmaz. Giriş bilgisi ve takip çerezi toplanmaz.",
 footerStage:"ÖN İNCELEME SÜRÜMÜ",selectCraft:"Sanat dalını seç"
 },
 en:{
 navExplore:"Explore crafts",navWorks:"Artworks",navStudio:"Digital studio",navMakers:"For makers",language:"Language",
 eyebrow:"NOT ONE ART FORM. A WHOLE CULTURAL ATLAS.",hero:"Preserving<br>the past.<br><em>Weaving</em><br>the future.",
 heroText:"From Ebru and ceramics to filigree, miniature painting, kilims and woodblock printing. Explore living Anatolian traditions and help shape a world connecting makers directly with audiences.",
 exploreButton:"Explore traditions",makerButton:"Join as a maker",heroNote:"Independent discovery · No fabricated makers, stock or sales",
 heroArt:"CULTURAL MAP / DIGITAL INTERPRETATION",statArts:"CRAFT DISCIPLINES",statLang:"LANGUAGES / TR · EN · DE",statOffer:"VERIFIED LIVE PRODUCT LINK",
 statCaption:"The number of traditions is not the number of listed products or verified makers.",
 exploreKicker:"CULTURAL DISCOVERY",exploreTitle:"Art is a <em>map.</em>",
 exploreLead:"Search traditional techniques and filter by purpose. Each card is a craft discipline, not a sales listing.",
 searchLabel:"Find an art or technique",searchPlaceholder:"e.g. weaving, Ebru, filigree",
 familyLabel:"Material / family",usageLabel:"How will you use it?",clear:"Reset filters ↺",
 allFamilies:"All craft families",paper:"Paper & book arts",ceramics:"Ceramics & tiles",textile:"Weaving & fibre",jewelry:"Jewellery & filigree",wood:"Wood arts",metal:"Metalwork",glass:"Glass arts",other:"Other crafts",
 allUses:"All purposes",wall:"Wall / art",home:"Home / interiors",wear:"Wearable",gift:"Gift",collect:"Collect",learn:"Learn",
 count:"craft disciplines",catalogNotice:"Cultural directory • Not product inventory",none:"No matches",noResults:"No matching crafts.",noResultsBody:"Try another craft term or purpose.",
 craftAvailable:"Existing product link",craftPending:"Awaiting verified maker / artwork",craftOpen:"See collection",craftDiscover:"Explore status",
 worksKicker:"VERIFIED LINKS / CURATION",worksTitle:"Art is not<br><em>a claim.</em>",
 worksLead:"Only collections with a known live sales link appear here. Confirm price, checkout, tax and digital delivery terms with the seller's platform.",
 offerTag:"LIVE KO-FI LISTING",offerDigital:"DIGITAL COLLECTION",offerBody:"Six digital Ebru art reproductions, printable files and a collection guide. Check license and delivery conditions directly at Ko-fi.",
 offerGo:"View on Ko-fi ↗",offerUnknown:"No verified live sales link for this craft selection yet.",offerUnknownTitle:"No verified listing yet",
 offerDisclaimer:"The product link exists. A completed payment or delivery is not claimed.",
 studioKicker:"FREE DIGITAL EXPERIENCE",studioTitle:"Let water hold<br><em>your first pattern.</em>",
 studioLead:"Drop colours, comb the surface and save your design as a PNG in your own browser. This is not physical Ebru craftsmanship.",
 studioAction:"Open digital Ebru studio",
 makerKicker:"ARTISAN / ARTIST / MAKER",makerTitle:"Become part<br>of <em>the atlas.</em>",
 makerLead:"Create a first draft of your maker listing in your own browser. Download your JSON; no account is created and nothing is published.",
 makerName:"Artist / studio name *",makerCraft:"Craft discipline *",makerCity:"City / region",
 makerDesc:"Describe your making process and artwork *",makerContact:"Contact (saved only in your draft file)",
 saveDraft:"Download maker draft",makerSuccess:"Draft downloaded. Nothing was submitted to a server.",
 makerError:"Check name, craft and a description of at least 20 characters.",
 makerNoteTitle:"Art first. Trust follows.",makerNote:"We never list your work or another maker's inventory without verification. Public maker accounts, direct messaging and marketplace checkout are not yet active.",
 makerNoteFoot:"BROWSER-ONLY DRAFT / NO SERVER SUBMISSION",
 footerManifesto:"Art has no borders. Craft holds memory.",footerDirectory:"DIRECTORY",footerTrust:"TRANSPARENCY",
 footerHonesty:"No invented sellers, products or sales. Checkout only at Ko-fi. No login or tracking cookies are collected.",
 footerStage:"PRIVATE REVIEW BUILD",selectCraft:"Select discipline"
 },
 de:{
 navExplore:"Handwerke entdecken",navWorks:"Kunstwerke",navStudio:"Digitales Atelier",navMakers:"Für Kunstschaffende",language:"Sprache",
 eyebrow:"NICHT NUR EINE KUNST. EIN GANZER KULTURATLAS.",hero:"Vergangenheit<br>bewahren.<br><em>Zukunft</em><br>weben.",
 heroText:"Von Ebru und Keramik bis zu Filigranschmuck, Miniaturmalerei, Kelims und Holzdruck: Entdecke lebendige anatolische Traditionen und eine Kulturwelt, die Menschen direkt verbindet.",
 exploreButton:"Kunsthandwerke entdecken",makerButton:"Als Künstler mitwirken",heroNote:"Unabhängiger Kulturatlas · Keine erfundenen Produkte oder Verkäufe",
 heroArt:"KULTURKARTE / DIGITALE INTERPRETATION",statArts:"KUNSTHANDWERKE",statLang:"SPRACHEN / TR · EN · DE",statOffer:"PRÜFBARER PRODUKTLINK",
 statCaption:"Die Zahl der Traditionen ist nicht die Zahl der Angebote oder bestätigten Anbieter.",
 exploreKicker:"KULTURELLE ENTDECKUNG",exploreTitle:"Kunst ist eine <em>Landkarte.</em>",
 exploreLead:"Traditionelle Techniken entdecken und nach Verwendungszweck filtern. Eine Disziplin ist noch kein Verkaufsangebot.",
 searchLabel:"Kunst oder Technik suchen",searchPlaceholder:"z. B. Weberei, Ebru, Filigran",
 familyLabel:"Material / Familie",usageLabel:"Wofür interessiert es dich?",clear:"Filter zurücksetzen ↺",
 allFamilies:"Alle Handwerksfamilien",paper:"Papier & Buch",ceramics:"Keramik & Fliesen",textile:"Weben & Fasern",jewelry:"Schmuck & Filigran",wood:"Holz",metal:"Metall",glass:"Glas",other:"Weitere Techniken",
 allUses:"Alle Zwecke",wall:"Wand / Kunst",home:"Wohnen",wear:"Tragbare Kunst",gift:"Geschenk",collect:"Sammeln",learn:"Lernen",
 count:"Kunsthandwerke",catalogNotice:"Kulturverzeichnis • Kein Warenbestand",none:"Keine Treffer",noResults:"Keine Treffer.",noResultsBody:"Versuche eine andere Kunstform oder Nutzung.",
 craftAvailable:"Bestehender Produktlink",craftPending:"Noch kein geprüftes Angebot",craftOpen:"Kollektion ansehen",craftDiscover:"Status ansehen",
 worksKicker:"PRÜFBARE LINKS / KURATION",worksTitle:"Kunst ist<br><em>kein Versprechen.</em>",
 worksLead:"Wir zeigen nur Kollektionen mit bekanntem Verkaufslink. Preis, Zahlung, Steuern und Lieferung sind beim Verkaufsanbieter zu prüfen.",
 offerTag:"KO-FI-ANGEBOT",offerDigital:"DIGITALE KOLLEKTION",offerBody:"Sechs digitale Ebru-Reproduktionen, druckbare Dateien und ein Kollektionsführer. Lizenz und Lieferung bitte direkt bei Ko-fi prüfen.",
 offerGo:"Auf Ko-fi ansehen ↗",offerUnknown:"Für diese Auswahl gibt es noch keinen geprüften Verkaufslink.",offerUnknownTitle:"Noch kein Angebot",
 offerDisclaimer:"Der Produktlink ist vorhanden. Es wird keine erfolgte Zahlung oder Lieferung behauptet.",
 studioKicker:"KOSTENLOSES DIGITALES ERLEBNIS",studioTitle:"Lass im Wasser<br><em>dein Muster</em> entstehen.",
 studioLead:"Farbtropfen setzen, kämmen und dein digitales Muster als PNG speichern. Das ist keine echte physische Ebru-Herstellung.",
 studioAction:"Digitales Ebru-Atelier öffnen",
 makerKicker:"KUNSTHANDWERK / ATELIER",makerTitle:"Werde Teil<br><em>des Atlas.</em>",
 makerLead:"Erstelle einen Entwurf deines Künstlerprofils direkt im Browser. Lade die JSON-Datei herunter – ohne Konto und ohne Veröffentlichung.",
 makerName:"Name des Ateliers / Künstlers *",makerCraft:"Handwerk *",makerCity:"Ort / Region",
 makerDesc:"Beschreibe Werk und Herstellungsweise *",makerContact:"Kontakt (nur in der Entwurfsdatei)",
 saveDraft:"Entwurf herunterladen",makerSuccess:"Entwurf gespeichert. Es wurden keine Daten übertragen.",
 makerError:"Bitte Namen, Handwerk und mindestens 20 Zeichen Beschreibung prüfen.",
 makerNoteTitle:"Erst Kunst. Dann Vertrauen.",makerNote:"Wir stellen keine Werke oder Händler ohne Prüfung ein. Öffentliche Konten, Nachrichten und Plattformzahlungen sind derzeit nicht aktiv.",
 makerNoteFoot:"NUR IM BROWSER / KEINE SERVERÜBERTRAGUNG",
 footerManifesto:"Kunst kennt keine Grenzen. Handwerk trägt Erinnerung.",footerDirectory:"VERZEICHNIS",footerTrust:"TRANSPARENZ",
 footerHonesty:"Keine erfundenen Händler, Angebote oder Verkäufe. Zahlungen ausschließlich bei Ko-fi. Kein Login oder Tracking-Cookies.",
 footerStage:"NICHT ÖFFENTLICHE PRÜFVERSION",selectCraft:"Handwerk wählen"
 }
};
const $=id=>document.getElementById(id);
const params=new URLSearchParams(window.location.search);
const langSelect=$("lang"),search=$("search"),family=$("family"),use=$("use");
let lang=normalizeLang(params.get("lang")),selectedCraft=null;
const label=(key)=>translations[lang][key]||translations.tr[key]||key;
const compose=(tag,klass,text)=>{const e=document.createElement(tag);if(klass)e.className=klass;if(text!==undefined)e.textContent=String(text);return e;};
function updateUrl(){
 const p=new URLSearchParams();
 if(lang!=="tr")p.set("lang",lang);
 if(search.value.trim())p.set("q",search.value.trim().slice(0,100));
 if(family.value!=="all")p.set("family",family.value);
 if(use.value!=="all")p.set("use",use.value);
 const suffix=p.size?"?"+p.toString():"";
 window.history.replaceState(null,"",window.location.pathname+suffix+window.location.hash);
}
function setLanguage(next){
 lang=normalizeLang(next);langSelect.value=lang;
 document.documentElement.lang=lang;
 document.querySelectorAll("[data-i18n]").forEach(el=>{el.textContent=label(el.dataset.i18n);});
 document.querySelectorAll("[data-i18n-html]").forEach(el=>{
  // Trusted static translations owned by this module; no user HTML.
  el.innerHTML=label(el.dataset.i18nHtml);
 });
 search.placeholder=label("searchPlaceholder");
 fillMakerSelect();
 render();
 updateUrl();
}
function fillMakerSelect(){
 const el=$("maker-craft"),prior=el.value;
 el.replaceChildren();
 const placeholder=compose("option","",label("selectCraft"));
 placeholder.value="";el.append(placeholder);
 for(const c of MEDIA){const opt=compose("option","",c[lang]);opt.value=c.id;el.append(opt);}
 if(MEDIA.some(x=>x.id===prior))el.value=prior;
}
function craftButton(c,index){
 const b=compose("button","craft");
 b.type="button";
 b.setAttribute("aria-label",c[lang]+": "+(listingForCraft(c.id).length?label("craftAvailable"):label("craftPending")));
 const ordinal=compose("span","number",String(index+1).padStart(2,"0")+" / "+c.family.toUpperCase());
 const icon=compose("span","symbol",["✥","✳","◈","❋","⌁"][index%5]);icon.setAttribute("aria-hidden","true");
 b.append(ordinal,icon,compose("h3","",c[lang]));
 b.append(compose("span","translation",lang==="tr"?c.en:c.tr));
 const foot=compose("div","foot");
 foot.append(compose("span",listingForCraft(c.id).length?"availability":"pending",listingForCraft(c.id).length?label("craftAvailable"):label("craftPending")));
 foot.append(compose("span","",listingForCraft(c.id).length?"↗":"→"));
 b.append(foot);
 b.addEventListener("click",()=>{
  selectedCraft=c.id;
  renderOffers();
  $("works").scrollIntoView({behavior:"smooth",block:"start"});
 });
 return b;
}
function renderOffers(){
 const container=$("offer-container");
 container.replaceChildren();
 const visibleCrafts=searchCrafts({q:search.value,family:family.value,use:use.value,lang});
 const ids=selectedCraft?[selectedCraft]:visibleCrafts.map(x=>x.id);
 const offers=visibleOffers(ids);
 if(offers.length===0){
  const section=compose("div","no-offer");
  section.append(compose("h3","",label("offerUnknownTitle")),compose("p","",label("offerUnknown")));
  container.append(section);
  return;
 }
 for(const offer of offers){
  const section=compose("article","offer");
  const art=compose("div","offer-art");
  art.setAttribute("role","img");
  art.setAttribute("aria-label","Abstract CSS study; not a photograph of the actual product");
  const info=compose("div","offer-info"),badges=compose("div","offer-top");
  badges.append(compose("span","",label("offerTag")),compose("span","",label("offerDigital")));
  const h=compose("h3","",offer.title);
  const desc=compose("p","",label("offerBody"));
  const disclaimer=compose("p","",label("offerDisclaimer"));
  const row=compose("div","offer-bottom");
  const price=compose("strong","",offer.priceNote);
  const a=compose("a","",label("offerGo"));a.href=offer.url;a.target="_blank";a.rel="noopener noreferrer";
  row.append(price,a);info.append(badges,h,desc,row,disclaimer);section.append(art,info);container.append(section);
 }
}
function render(){
 const crafts=searchCrafts({q:search.value,family:family.value,use:use.value,lang});
 const list=$("craft-list");list.replaceChildren();
 crafts.forEach((c,i)=>list.append(craftButton(c,i)));
 $("count").textContent=crafts.length+" "+label("count");
 $("empty").hidden=crafts.length!==0;
 renderOffers();
}
function filtersChanged(){
 selectedCraft=null;
 render();updateUrl();
}
function init(){
 search.value=(params.get("q")||"").slice(0,100);
 family.value=normalizeFilter(params.get("family"),FAMILIES);
 use.value=normalizeFilter(params.get("use"),FILTERS);
 setLanguage(lang);
 langSelect.addEventListener("change",()=>setLanguage(langSelect.value));
 search.addEventListener("input",filtersChanged);
 family.addEventListener("change",filtersChanged);
 use.addEventListener("change",filtersChanged);
 $("reset").addEventListener("click",()=>{
  search.value="";family.value="all";use.value="all";selectedCraft=null;filtersChanged();
 });
 $("maker-form").addEventListener("submit",event=>{
  event.preventDefault();
  const status=$("maker-status");
  try{
   const draft=makeMakerDraft({
    name:$("maker-name").value,
    craft:$("maker-craft").value,
    city:$("maker-city").value,
    description:$("maker-description").value,
    contact:$("maker-contact").value,lang
   });
   const blob=new Blob([JSON.stringify(draft,null,2)+"\n"],{type:"application/json"});
   const url=URL.createObjectURL(blob),a=document.createElement("a");
   a.href=url;a.download="anatolian-atlas-maker-draft.json";document.body.append(a);a.click();a.remove();
   setTimeout(()=>URL.revokeObjectURL(url),0);
   status.textContent=label("makerSuccess");status.dataset.state="success";
  }catch{
   status.textContent=label("makerError");status.dataset.state="error";
  }
 });
 // Explicit fail-closed constraint: the catalog cannot assert actual sales.
 if(confirmedSalesFromCatalog()!==null)throw new Error("Catalog must not infer revenue");
}
init();
