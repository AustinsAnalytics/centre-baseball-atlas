// A saved release instant, not the visitor's current time or source-data cutoff.
export function releaseLabel(value){
 if(typeof value!=='string'||!/(Z|[+-]\d{2}:\d{2})$/.test(value))return null;
 const date=new Date(value);if(!Number.isFinite(date.getTime()))return null;
 const timeZone='America/New_York';
 const day=new Intl.DateTimeFormat('en-US',{timeZone,month:'short',day:'numeric',year:'numeric'}).format(date);
 const time=new Intl.DateTimeFormat('en-US',{timeZone,hour:'numeric',minute:'2-digit',hour12:true,timeZoneName:'short'}).format(date);
 return `${day} · ${time}`.replace(/\s/g,' ');
}
