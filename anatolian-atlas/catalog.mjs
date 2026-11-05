/**
 * Anatolian Atlas — broad cultural taxonomy and truthful sellable inventory.
 * Taxonomy names are disciplines, NOT claims about verified vendors/products.
 * This module is also the source of truth for browser + dependency-free tests.
 */
export const MEDIA=[
 ["ebru","Ebru","Water marbling","Marmorierkunst","paper",["wall","learn","gift"]],
 ["cini","Çini","Painted tiles","Fliesenkunst","ceramics",["wall","collect","gift"]],
 ["seramik","Seramik","Ceramics","Keramik","ceramics",["home","collect","gift"]],
 ["kilim","Kilim","Flatwoven kilims","Kilimweberei","textile",["home","collect","gift"]],
 ["hali","Halı","Carpet weaving","Teppichweberei","textile",["home","collect"]],
 ["dokuma","Dokuma","Traditional weaving","Webkunst","textile",["home","wear","learn"]],
 ["kece","Keçe","Felt making","Filzkunst","textile",["home","wear","learn"]],
 ["oya","Oya","Lace & needlework","Nadelspitze","textile",["wear","gift","collect"]],
 ["telkari","Telkâri","Filigree metalwork","Filigranschmuck","jewelry",["wear","collect","gift"]],
 ["takicilik","Takı sanatları","Jewelry traditions","Schmuckhandwerk","jewelry",["wear","gift"]],
 ["minyatur","Minyatür","Miniature painting","Miniaturmalerei","paper",["wall","collect","learn"]],
 ["tezhip","Tezhip","Manuscript illumination","Buchillumination","paper",["wall","learn","collect"]],
 ["hat","Hat","Calligraphy","Kalligrafie","paper",["wall","learn","gift"]],
 ["ahsap-baski","Ahşap baskı","Woodblock printing","Holzdruck","wood",["wall","learn","gift"]],
 ["oymacilik","Ahşap oymacılığı","Wood carving","Holzschnitzerei","wood",["home","collect"]],
 ["kakma","Sedef kakma","Mother-of-pearl inlay","Perlmutt-Einlegearbeit","wood",["home","collect","gift"]],
 ["bakir","Bakırcılık","Coppersmithing","Kupferhandwerk","metal",["home","collect","gift"]],
 ["demir","Demir işlemeciliği","Metal forging","Metallschmiedekunst","metal",["home","collect"]],
 ["cam","Cam sanatı","Glass arts","Glaskunst","glass",["home","collect","gift"]],
 ["nazar","Cam boncuk","Glass beadwork","Glasperlenkunst","glass",["wear","gift"]],
 ["deri","Deri işçiliği","Leather craft","Lederhandwerk","other",["wear","home","collect"]],
 ["ebru-cilt","Kitap ciltçiliği","Bookbinding","Buchbindekunst","paper",["collect","learn","gift"]],
 ["tasin-izi","Taş işçiliği","Stone carving","Steinbildhauerei","other",["home","collect"]],
 ["sepet","Sepet örücülüğü","Basket weaving","Korbflechterei","other",["home","learn"]]
].map(([id,tr,en,de,family,uses])=>Object.freeze({id,tr,en,de,family,uses:Object.freeze(uses)}));
export const FILTERS=Object.freeze(["all","wall","home","wear","gift","collect","learn"]);
export const FAMILIES=Object.freeze(["all","paper","ceramics","textile","jewelry","wood","metal","glass","other"]);
export const OFFERS=Object.freeze([
 Object.freeze({
  id:"ebru-studies-vol-1",
  craft:"ebru",
  title:"Ebru Studies Vol. 1",
  priceNote:"€18+",
  provider:"Ko-fi",
  kind:"digital",
  verifiedLiveListing:true,
  independentlyVerifiedPayment:false,
  independentlyVerifiedDelivery:false,
  url:"https://ko-fi.com/s/8f756c2778",
  use:["wall","gift"],
  note:"Six digital art reproductions; buyer verifies current listing and delivery terms at Ko-fi."
 })
]);
export const LANGS=Object.freeze(["tr","en","de"]);
export function normalizeLang(value){return LANGS.includes(value)?value:"tr";}
export function normalizeFilter(value,allowed){return allowed.includes(value)?value:"all";}
export function searchCrafts({q="",family="all",use="all",lang="tr"}={}){
 const safeLang=normalizeLang(lang), term=String(q).toLocaleLowerCase(safeLang).trim().slice(0,100);
 const type=normalizeFilter(family,FAMILIES),purpose=normalizeFilter(use,FILTERS);
 return MEDIA.filter(c=>(type==="all"||c.family===type)
   && (purpose==="all"||c.uses.includes(purpose))
   && (!term||[c.id,c.tr,c.en,c.de,c.family].some(v=>v.toLocaleLowerCase(safeLang).includes(term))));
}
export function listingForCraft(id){
 return OFFERS.filter(x=>x.craft===id&&x.verifiedLiveListing===true);
}
export function visibleOffers(craftIds){
 if(!Array.isArray(craftIds))throw new TypeError("Expected array");
 return OFFERS.filter(x=>x.verifiedLiveListing&&craftIds.includes(x.craft));
}
export function makeMakerDraft({name="",craft="",city="",description="",contact="",lang="tr"}={}){
 const clean=(value,max)=>String(value??"").trim().slice(0,max);
 const id=clean(craft,70);
 if(!MEDIA.some(x=>x.id===id))throw new Error("Choose existing craft");
 const shortName=clean(name,100), statement=clean(description,1000);
 if(shortName.length<2||statement.length<20)throw new Error("Name and honest description required");
 return {
  schema:"anatolian-atlas.maker-draft.v1",
  publication_status:"OWNER_REVIEW_REQUIRED_NOT_SENT",
  title:shortName,craft_id:id,
  location_text:clean(city,100),description:statement,contact_draft:clean(contact,150),
  language:normalizeLang(lang),
  terms:"Draft only. No account created, buyer inquiry sent, approval implied or goods listed.",
  rights_and_authenticity_unverified:true,
  inventory_unverified:true,
  no_server_transmission:true
 };
}
export function confirmedSalesFromCatalog(){
 // Link existence does not establish orders or settlement.
 return null;
}
