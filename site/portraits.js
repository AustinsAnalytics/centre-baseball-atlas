import{esc}from'./metrics.js';
export const portraitKey=p=>`${p.team}|${p.name}`;
export function portraitFor(p,catalog){return catalog?.players?.[portraitKey(p)]||null}
export function portrait(p,catalog,size='card'){
 const photo=portraitFor(p,catalog),initials=(p.display||p.name||'?').split(' ').filter(Boolean).map(s=>s[0]).slice(0,2).join('');
 let image='';
 if(photo){const[x,y,edge]=photo.crop,style=`width:${photo.width/edge*100}%;height:${photo.height/edge*100}%;left:${-x/edge*100}%;top:${-y/edge*100}%;`;image=`<img data-portrait src="${esc(photo.file)}" alt="" loading="${size==='hero'?'eager':'lazy'}" decoding="async" width="${photo.width}" height="${photo.height}" style="${style}">`}
 return `<span class="portrait portrait-${size}${photo?' has-photo':''}" aria-hidden="true"><span class="portrait-initials">${esc(initials)}</span>${image}</span>`;
}
export function portraitCredit(p,catalog){const photo=portraitFor(p,catalog);if(!photo)return '';return `<p class="portrait-credit">Photo: ${photo.sourcePage?`<a href="${esc(photo.sourcePage)}" target="_blank" rel="noopener noreferrer">${esc(photo.credit)} ↗</a>`:'provided photo'}${photo.sourceType==='sewanee'||photo.sourceType==='mount'?' · previous school':''}</p>`}
export function installPortraitFallback(root=document){root.addEventListener('error',e=>{const img=e.target;if(img?.matches?.('img[data-portrait]')){img.closest('.portrait')?.classList.add('portrait-failed');img.remove()}},true)}
