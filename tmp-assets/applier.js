window.__dec=(s)=>{const t=document.createElement('textarea');t.innerHTML=s;return t.value};
window.__plainP=(inner)=>__dec(inner.replace(/<[^>]+>/g,'')).replace(/\s+/g,' ').trim();
window.__applyPara=(inner,after)=>{
 const toks=[];for(const m of inner.matchAll(/(<[^>]+>)|([^<]+)/g)){if(m[1])toks.push({tag:m[1]});else{for(const p of __dec(m[2]).match(/\s+|\S+/g)||[])toks.push(/^\s+$/.test(p)?{sp:p}:{w:p})}}
 const W=[];let pre='';for(const t of toks){if(t.sp)pre+=t.sp;else if(t.w){t.pre=pre;pre='';W.push(t)}else if(t.tag&&!/^<\//.test(t.tag)){t.pre=pre;pre=''}}
 const A=after.trim().split(/\s+/);const B=W.map(t=>t.w);const n=B.length,m=A.length;
 const L=Array.from({length:n+1},()=>new Int16Array(m+1));for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L[i][j]=B[i]===A[j]?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
 let i=0,j=0;const ins={};let lastW=-1;
 while(i<n||j<m){if(i<n&&j<m&&B[i]===A[j]){W[i].keep=true;lastW=i;i++;j++}else if(i<n&&(j>=m||L[i+1][j]>=L[i][j+1])){W[i].del=true;lastW=i;i++}else{(ins[lastW]=ins[lastW]||[]).push(A[j]);j++}}
 let out='';const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');let first=true;
 const emitIns=(k)=>{for(const w of (ins[k]||[])){out+=(first?'':' ')+esc(w);first=false}};
 emitIns(-1);let wi=0;
 for(const t of toks){if(t.tag){if(!/^<\//.test(t.tag)&&t.pre&&!first){out+=' ';t._sp=1}out+=t.tag;continue}if(t.sp)continue;if(t.w){const idx=W.indexOf(t);if(t.keep){out+=((first||(t.pre===''&&!t._x))?(first?'':t.pre):' ')+esc(t.w);first=false}emitIns(idx)}}
 return out.replace(/ +/g,' ').replace(/(<a[^>]*>|<strong>|<em>) /g,' $1').replace(/ (<\/a>|<\/strong>|<\/em>)/g,'$1 ').replace(/ +/g,' ').replace(/ ([,.;:!?)”’])/g,'$1').replace(/^ /,'').replace(/ $/,'')};
window.__applyArticle=async(id,afterParas,dry)=>{const p=await (await fetch('/wp-json/wp/v2/posts/'+id+'?context=edit&_fields=content',{headers:{'X-WP-Nonce':__n}})).json();let raw=p.content.raw;
 const ps=[...raw.matchAll(/(<p\b[^>]*>)([\s\S]*?)(<\/p>)/g)];const report=[];let out=raw;let offset=0;
 for(const [bef,aft] of afterParas){const hit=ps.filter(x=>__plainP(x[2])===bef);if(hit.length!==1){report.push('MATCH '+hit.length+': '+bef.slice(0,40));continue}const x=hit[0];const neu=__applyPara(x[2],aft);
  const chk=__plainP(neu);if(chk!==aft.replace(/\s+/g,' ').trim())report.push('TEXT MISMATCH: '+aft.slice(0,40)+' || got: '+chk.slice(0,200));
  const anchors=[...neu.matchAll(/<a\b[^>]*>([\s\S]*?)<\/a>/g)].map(a=>a[1].replace(/<[^>]+>/g,''));report.push('A: '+anchors.map(a=>'['+a+']').join(' '));
  out=out.replace(x[1]+x[2]+x[3],x[1]+neu+x[3])}
 window.__out=out;if(!dry){const r=await fetch('/wp-json/wp/v2/posts/'+id+'?_fields=id',{method:'POST',headers:{'X-WP-Nonce':__n,'Content-Type':'application/json'},body:JSON.stringify({content:out})});report.push('SAVE '+r.status)}return report.join('\n')};
'ok'
