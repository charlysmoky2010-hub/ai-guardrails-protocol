import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,existsSync} from "node:fs";
import {MEDIA,OFFERS,FAMILIES,FILTERS,LANGS,searchCrafts,visibleOffers,listingForCraft,makeMakerDraft,confirmedSalesFromCatalog} from "./catalog.mjs";
const path=new URL("./",import.meta.url);
const html=readFileSync(new URL("index.html",path),"utf8");
const client=readFileSync(new URL("atlas.mjs",path),"utf8");
test("real atlas spans 24 unique cultural traditions, no invented vendor stock",()=>{
 assert.equal(MEDIA.length,24);
 assert.equal(new Set(MEDIA.map(c=>c.id)).size,24);
 for(const c of MEDIA){
  assert.ok(c.tr&&c.en&&c.de&&c.family);
  assert.ok(c.uses.length>=1);
  assert.ok(FAMILIES.includes(c.family));
  assert.ok(c.uses.every(x=>FILTERS.includes(x)));
 }
 for(const id of ["ebru","cini","seramik","kilim","hali","dokuma","telkari","minyatur","ahsap-baski","hat","tezhip","cam","bakir","kece","oya"])
   assert.ok(MEDIA.some(c=>c.id===id));
});
test("one live Ko-fi product link is not a count of completed sales",()=>{
 assert.equal(OFFERS.length,1);
 assert.equal(OFFERS[0].id,"ebru-studies-vol-1");
 assert.equal(OFFERS[0].url,"https://ko-fi.com/s/8f756c2778");
 assert.equal(OFFERS[0].provider,"Ko-fi");
 assert.equal(OFFERS[0].independentlyVerifiedPayment,false);
 assert.equal(OFFERS[0].independentlyVerifiedDelivery,false);
 assert.equal(confirmedSalesFromCatalog(),null);
 for(const c of MEDIA)if(c.id!=="ebru")assert.equal(listingForCraft(c.id).length,0);
});
test("searches in Turkish German English with material and purpose filters",()=>{
 for(const [query,lang,id] of [["ebru","tr","ebru"],["filigree","en","telkari"],["Filigran","de","telkari"],["dokuma","tr","dokuma"],["Keramik","de","seramik"]]){
  assert.ok(searchCrafts({q:query,lang}).some(x=>x.id===id));
 }
 assert.ok(searchCrafts({family:"textile"}).length>=4);
 assert.ok(searchCrafts({use:"learn"}).length>=5);
 assert.ok(searchCrafts({family:"textile",use:"learn"}).every(x=>x.family==="textile"&&x.uses.includes("learn")));
 assert.deepEqual(searchCrafts({q:"not-a-real-craft-text"}),[]);
});
test("filters never invent new offers",()=>{
 const ids=searchCrafts({family:"metal"}).map(x=>x.id);
 assert.deepEqual(visibleOffers(ids),[]);
 assert.equal(visibleOffers(["ebru"]).length,1);
 assert.throws(()=>visibleOffers({invalid:true}),TypeError);
});
test("maker draft is locally owned and explicitly not a published maker listing",()=>{
 const x=makeMakerDraft({
  name:"Anatolian Workshop",craft:"telkari",city:"Mardin",
  description:"Original handmade filigree jewelry with direct artist oversight.",
  contact:"private@example.org",lang:"en"
 });
 assert.equal(x.publication_status,"OWNER_REVIEW_REQUIRED_NOT_SENT");
 assert.equal(x.no_server_transmission,true);
 assert.equal(x.rights_and_authenticity_unverified,true);
 assert.equal(x.inventory_unverified,true);
 assert.equal(x.craft_id,"telkari");
 assert.equal(x.contact_draft,"private@example.org");
});
test("invalid or empty maker listings fail closed",()=>{
 assert.throws(()=>makeMakerDraft({name:"A",craft:"ebru",description:"A sufficiently detailed description."}));
 assert.throws(()=>makeMakerDraft({name:"Artist",craft:"fictional",description:"A sufficiently detailed description."}));
 assert.throws(()=>makeMakerDraft({name:"Artist",craft:"ebru",description:"Short"}));
});
test("all languages remain supported with no paid checkout embedded in our page",()=>{
 assert.deepEqual(LANGS,["tr","en","de"]);
 for(const id of ["lang","search","family","use","craft-list","offer-container","maker-form","maker-status"])
  assert.ok(html.includes('id="'+id+'"'));
 assert.ok(html.includes('content="noindex,nofollow"'));
 assert.ok(html.includes('href="./studio/"'));
 assert.ok(existsSync(new URL("./studio/index.html",path)));
 assert.ok(client.includes('URL.createObjectURL(blob)'));
 assert.ok(!client.includes("fetch("));
 assert.ok(!client.includes("navigator.sendBeacon"));
});
