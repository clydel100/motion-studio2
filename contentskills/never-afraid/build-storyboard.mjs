// Writes storyboard.json for "never-afraid". Edit this file, not the JSON, then: node projects/never-afraid/build-storyboard.mjs
import {writeFileSync} from 'node:fs';
const T = 'lines-of-light';
// text titles are built for 5-6.5 s; these lines run about 2.5 s, so their animation plays faster to land on the words
const SPEED = {'text/keyword-slam': 1.6, 'text/headline-slam': 1.8, 'text/end-card': 1.6};
const bg = (piece, props = {}) => ({piece, props, ...(piece.startsWith('text/') ? {speed: SPEED[piece] ?? 2.4} : {})});
const shot = (id, narration, title, candidates, extra = {}) => ({id, narration, candidates, ...extra});  // title kept here as a note only: a shot title draws a headline over the piece

const shots = [
  shot('hook', 'You were never meant to live afraid.', 'Never meant to live afraid', [
    {background: bg('text/headline-slam', {lines: ['NEVER', 'AFRAID'], kicker: '', note: '', labels: ['', '', '', ''], foot: [''], field: 'teal'})},
    {background: bg('text/split-stack', {top: 'NEVER', bottom: 'AFRAID', caption: 'YOU WERE NEVER\nMEANT TO LIVE', note: '', labels: ['', '', '', ''], field: 'black'})},
  ]),
  shot('egg', "A farmer once found an eagle's egg", "A farmer finds an eagle's egg", [
    {background: bg('three/light-torus')},
    {background: bg('three/wire-globe')},
  ]),
  shot('hen', 'and set it under a hen.', 'Hidden under a hen', [
    {background: bg('text/keyword-slam', {word: 'UNDER A HEN', kicker: 'RAISED AS SOMETHING ELSE', y: 760})},
    {background: bg('text/statement', {statement: 'He set it under a hen', emphasis: ['HEN'], tag: 'A PARABLE', labels: ['', '', '', ''], foot: '', field: 'deep'})},
  ]),
  shot('dirt', 'The eagle grew up in the dirt with the chickens.', 'Growing up in the dirt', [
    {background: bg('three/grid-horizon')},
    {background: bg('text/marquee-wall', {field: 'black'})},
  ]),
  shot('shadow', 'Every time a shadow crossed the sky, it ran and hid.', 'Running from every shadow', [
    {background: bg('three/wire-tunnel')},
    {background: bg('text/keyword-slam', {word: 'IT HID', kicker: 'EVERY SHADOW', y: 760})},
  ]),
  shot('soaring', 'One day it looked up and saw an eagle soaring.', 'It looks up and sees an eagle', [
    {background: bg('three/light-beam')},
    {background: bg('three/orbit-ribbons')},
  ]),
  shot('dream', '"Don\'t even dream it," the chickens said.', '"Don\'t even dream it"', [
    {background: bg('text/quote-card', {quote: "Don't even dream it", by: 'THE CHICKENS', role: 'EVERY VOICE OF FEAR', labels: ['', '', '', ''], field: 'ember'})},
    {background: bg('text/statement', {statement: "Don't even dream it", emphasis: ['DREAM'], tag: 'THE CHICKENS', labels: ['', '', '', ''], foot: '', field: 'ember'})},
  ]),
  shot('died', 'So it lived afraid, and died a chicken.', 'It lived afraid', [
    {background: bg('text/split-stack', {top: 'LIVED', bottom: 'AFRAID', caption: 'AND DIED\nA CHICKEN', note: '', labels: ['', '', '', ''], field: 'black'})},
    {background: bg('text/keyword-slam', {word: 'DIED A CHICKEN', kicker: 'SO IT LIVED AFRAID', y: 760})},
  ], {transition: {name: 'red_blue_cut', seconds: 0.5}}),
  shot('hear', 'Hear me.', 'Hear me', [
    {background: bg('text/keyword-slam', {word: 'HEAR ME', kicker: 'NOW', y: 760})},
    {background: bg('three/light-strands')},
  ]),
  shot('training', "Fear is not your nature. It's your training.", 'Fear is training, not nature', [
    {background: bg('text/versus', {a: 'NATURE', b: 'TRAINING', mark: 'VS', aNote: 'WHO YOU ARE', bNote: 'WHAT YOU LEARNED', labels: ['', '', '', ''], field: 'teal'})},
    {background: bg('text/split-stack', {top: 'NOT NATURE', bottom: 'TRAINING', caption: 'FEAR IS', note: '', labels: ['', '', '', ''], field: 'teal'})},
  ]),
  shot('spirit', 'God has not given you a spirit of fear,', 'No spirit of fear', [
    {background: bg('text/quote-card', {quote: 'God has not given you a spirit of fear', by: '2 TIMOTHY 1:7', role: 'THE WORD', labels: ['', '', '', ''], field: 'deep'})},
    {background: bg('text/statement', {statement: 'God has not given you a spirit of fear', emphasis: ['FEAR'], tag: '2 TIMOTHY 1:7', labels: ['', '', '', ''], foot: '', field: 'deep'})},
  ]),
  shot('power', 'but of power, love, and a sound mind.', 'Power, love, a sound mind', [
    {background: bg('text/agenda', {title: 'BUT OF', kicker: '2 TIMOTHY 1:7', items: ['POWER', 'LOVE', 'A SOUND MIND'], labels: ['', '', '', ''], step: .7, field: 'teal'})},
    {background: bg('three/light-beam')},
  ]),
  shot('identity', 'Your identity was never in the dirt.', 'Identity was never in the dirt', [
    {background: bg('text/statement', {statement: 'Your identity was never in the dirt', emphasis: ['IDENTITY'], tag: 'HEAR THIS', labels: ['', '', '', ''], foot: '', field: 'teal'})},
    {background: bg('text/keyword-slam', {word: 'IDENTITY', kicker: 'NEVER IN THE DIRT', y: 760})},
  ]),
  shot('christ', "It's in Christ.", 'It is in Christ', [
    {background: bg('three/light-beam'), visual: {piece: 'text/keyword-slam', speed: 1.6, props: {word: 'IN CHRIST', kicker: 'YOUR IDENTITY IS', y: 520}}},
    {background: bg('text/keyword-slam', {word: 'IN CHRIST', kicker: 'YOUR IDENTITY IS', y: 760})},
  ], {transition: {name: 'ray_burst', seconds: 0.6}}),
  shot('name', 'Stop rehearsing your fear. Start remembering your name.', 'Remember your name', [
    {background: bg('text/versus', {a: 'REHEARSE FEAR', b: 'REMEMBER NAME', mark: 'VS', aNote: 'STOP', bNote: 'START', labels: ['', '', '', ''], field: 'teal'})},
    {background: bg('text/split-stack', {top: 'STOP FEAR', bottom: 'YOUR NAME', caption: 'REMEMBER', note: '', labels: ['', '', '', ''], field: 'teal'})},
  ]),
  shot('cta', "You were born for the sky. Comment IDENTITY if you're ready to fly.", 'Born for the sky: comment IDENTITY', [
    {background: bg('text/end-card', {lines: ['COMMENT', 'IDENTITY'], action: 'YOU WERE BORN FOR THE SKY', handle: '', strip: 'READY TO FLY', labels: ['', '', '', ''], field: 'teal'})},
    {background: bg('three/grid-horizon')},
  ]),
];

const storyboard = {
  title: 'You were never meant to live afraid',
  theme: T,
  format: {width: 1080, height: 1920, fps: 30},
  captions: 'landing',
  lead: 0,
  room: {scale: 0.8, origin: '50% 13%'},  // keep every graphic clear of the app's caption and buttons at the bottom
  voice: {provider: 'kokoro', voice: 'af_maple', speed: 1.0},
  sections: [
    {id: 'hook', title: 'Never meant to live afraid', shots: ['hook'], job: 'hook'},
    {id: 'parable', title: 'The eagle raised among chickens', shots: ['egg', 'hen', 'dirt', 'shadow', 'soaring', 'dream', 'died'], job: 'demo'},
    {id: 'turn', title: 'Fear is training, not nature', shots: ['hear', 'training', 'spirit', 'power'], job: 'turn'},
    {id: 'payoff', title: 'Your identity is in Christ', shots: ['identity', 'christ', 'name'], job: 'payoff'},
    {id: 'ask', title: 'Comment IDENTITY', shots: ['cta'], job: 'ask'},
  ],
  shots,
};
writeFileSync(new URL('./storyboard.json', import.meta.url), JSON.stringify(storyboard, null, 1) + '\n');
console.log(`wrote storyboard.json: ${shots.length} shots`);
