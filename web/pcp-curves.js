"use strict";
const adoptionBand = d => d.internet_users_share_pct < 40 ? 0 : d.internet_users_share_pct < 70 ? 1 : 2;
// Two cubic segments per gap; measured axis intersections never move.
// Clamp the bundle midpoint between the endpoints to avoid artificial humps.
function countryCurve(xs,ys,center,strength){
  let p=`M ${xs[0]} ${ys[0]}`;
  for(let i=0;i<xs.length-1;i++){
    if(strength===0){p+=` L ${xs[i+1]} ${ys[i+1]}`;continue;}
    const dx=xs[i+1]-xs[i],m=(xs[i]+xs[i+1])/2;
    const raw=(ys[i]+ys[i+1])/2*(1-strength)+(center[i]+center[i+1])/2*strength;
    const ym=Math.max(Math.min(ys[i],ys[i+1]),Math.min(Math.max(ys[i],ys[i+1]),raw));
    p+=` C ${xs[i]+dx*.18} ${ys[i]}, ${m-dx*.16} ${ym}, ${m} ${ym}`;
    p+=` C ${m+dx*.16} ${ym}, ${xs[i+1]-dx*.18} ${ys[i+1]}, ${xs[i+1]} ${ys[i+1]}`;
  }
  return p;
}
if(typeof module!=="undefined")module.exports={adoptionBand,countryCurve};
