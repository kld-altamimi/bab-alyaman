// campaign.js - the whole campaign as the map shows it: the road from the Strait of Bab al-Mandab to the old city of
// Sana'a, with its forks, and one mission nobody is supposed to know about yet.
//
//   The Strait ── The Coffee Port ─┬─ coast road ─── The Souq ── The Islands ─┬─ The Terraces ─────┬── Bab al-Yemen ·· ???
//   (Bab al-Mandab)  (Mocha)       │                 (Zabid)     (Hodeidah)    └─ The Stone Bridge ─┤   (Sana'a)
//                                  │                                            (Haraz, Kawkaban)  │
//                                  └─ mountain road ─ The Castle ── The Green Valleys ── The Wadi ─┘
//                                                     (Taiz)        (Ibb)                (Dhamar)
//
// One go through the campaign is six missions; the forks decide which six. A mission opens when any road into it has
// been cleared. The Strait, the Coffee Port and the Souq are built so far: the others, once their road is open, wait as COMING SOON.
//   name: what the mission is called (the big name, on the map and the card); place: where it is, written under it;
//   stage: its number on the map (0 for the secret one); road: which way it lies; next: the roads out of it;
//   brief: what the briefing says; parts: the checkpoints it is played in; boss: what waits at the end of it.
// The Zanabeel (the Scorpion's foot soldiers; renamed from the Dhanabs on 19 Oct) hold the country; they chose the name themselves and wear it with
// pride, never hearing what it says. The Scorpion is their Uncle across the water: never seen, only his tail reaches Yemen.
//   label: where the name goes [dx, dy, align] (dy is the top of the name; the place goes under it); land: where the
//   picture of the place stands [dx, dy]; stamp: where CLEAR is stamped [dx, dy]; bow: how each road out of it curves;
//   sign: where a fork's signpost stands. (Where each mission is on the map comes from the art: ATLAS.menu.map.nodes.)
var CAMPAIGN = (function () {
  'use strict';
  return [
    { id: 'm1', stage: 1, name: 'The Strait', place: 'Bab al-Mandab', road: 'The landing', built: true, next: ['mocha'], bow: [-0.15],
      label: [13, 0, 'l'], land: [36, -4], stamp: [-30, 18],
      brief: 'The Zanabeel have parked a missile battery on the coast of the strait and dug in along the beach, under a banner that says who they are. Salem is bringing the truck. Try not to scratch it.',
      parts: ['Landfall', 'The fishing camp', 'Container beach', 'The coast road', 'The battery'],
      boss: 'A flying boat with four rotors and a lot of bombs, and the Commander watching from his tower. He is very proud of it. It was a gift.' },
    { id: 'mocha', stage: 2, name: 'The Coffee Port', place: 'Mocha', road: 'Up the coast', built: true, next: ['taiz'], bow: [0.1],      // (one road on: the Castle, then the Souq; Khaled, 22 Oct)
      label: [-14, -18, 'r'], land: [-22, 28], stamp: [-30, 14],
      brief: 'The port that gave coffee its name. The Zanabeel have seized every sack in the warehouses for the Scorpion, and the whole country is getting grumpy.',
      parts: ['The quay', 'The warehouses', 'The roasting house', 'The old lighthouse'],
      boss: 'The Big Roaster: a tank built round a coffee roaster. It is very hot, and it smells wonderful.' },
    { id: 'zabid', stage: 4, name: 'The Souq', place: 'Zabid', road: 'Coast road', built: true, next: ['hodeidah', 'ibb'], bow: [-0.14, 0.12], sign: [20, -6],
      label: [-12, -7, 'r'], land: [24, 2], stamp: [-30, 12],
      brief: 'The old town on the plain: white walls, a market in every alley, a Zanabeel checkpoint in every market, and a spice stall that will not survive the afternoon.',
      parts: ['The town gate', 'The spice stalls', 'The rooftops', 'The covered market'],
      boss: 'The Tailor: the Zanabeel\'s tailor, hiding among his own dummies, every one of them dressed exactly like him. Only one of them sneezes.' },
    { id: 'hodeidah', stage: 5, name: 'The Islands', place: 'Hodeidah', road: 'Coast road', built: false, next: ['haraz', 'kawkaban'], bow: [0.12, -0.1], sign: [20, -4],
      label: [-14, 2, 'r'], land: [-12, -10], stamp: [-30, 18],
      brief: 'The big port on the Red Sea, and the islands off it. The Zanabeel navy is four fishing boats and a ferry, all four flying the scorpion flag. Salem has borrowed a boat. Do not ask whose.',
      parts: ['The container yard', 'The crossing', 'The fishing village', 'The ferry'],
      boss: 'The ferry, which somebody has fitted with a gun turret and a horn you can hear in Djibouti.' },
    { id: 'haraz', stage: 6, name: 'The Terraces', place: 'Haraz', road: 'Mountain pass', built: false, next: ['sanaa'], bow: [0.12],
      label: [0, 11, 'c'], land: [-24, -4], stamp: [30, 12],
      brief: 'The road up from the coast climbs the Haraz mountains, terrace by green terrace, and the Zanabeel have dug in on every one of them.',
      parts: ['The foot of the mountain', 'The lower terraces', 'Manakhah', 'The pass'],
      boss: 'The goods lift: a cable car with a cannon in it, going up and down and up and down.' },
    { id: 'kawkaban', stage: 6, name: 'The Stone Bridge', place: 'Kawkaban', road: 'Northern road', built: false, next: ['sanaa'], bow: [0.1],
      label: [-12, -9, 'r'], land: [-2, -12], stamp: [-28, 12],
      brief: 'A fortress town on top of a cliff, and one way up to it: an old stone bridge between two peaks. The Zanabeel hold the far side. Do not look down.',
      parts: ['Shibam, at the foot', 'The cliff path', 'Across the bridge', 'The fortress gate'],
      boss: 'The Bridge Walker: far too heavy for the bridge, and far too stubborn to notice.' },
    { id: 'taiz', stage: 3, name: 'The Castle', place: 'Taiz', road: 'Mountain road', built: true, next: ['zabid'], bow: [0.12],      // (Mission 3; then down to the Souq, Mission 4: Khaled, 22 Oct)
      label: [13, -1, 'l'], land: [-4, 24], stamp: [30, -12],
      brief: 'A city on the slopes of a mountain, with a castle above it and the Zanabeel inside the castle. Everything in Taiz is uphill, so Salem has borrowed a helicopter.',
      parts: ['The lower town', 'The old market', 'The castle road', 'The keep'],
      boss: 'The Castle Gun: an old cannon the Zanabeel found in the castle, with a new engine bolted on.' },
    { id: 'ibb', stage: 5, name: 'The Green Valleys', place: 'Ibb', road: 'Mountain road', built: false, next: ['dhamar'], bow: [-0.12],
      label: [13, -3, 'l'], land: [-28, -2], stamp: [28, 16],
      brief: 'The greenest place in Yemen: terraces, waterfalls and rain. Yazeed has never been this wet, and the Zanabeel have never been this muddy.',
      parts: ['The valley road', 'The waterfall', 'The terraces', 'The town'],
      boss: 'The Mud Tank, which got stuck in the valley last week and has been firing at everyone ever since.' },
    { id: 'dhamar', stage: 6, name: 'The Wadi', place: 'Dhamar', road: 'Mountain road', built: false, next: ['sanaa'], bow: [0.12],
      label: [-12, -3, 'r'], land: [28, 8], stamp: [26, 22],
      brief: 'A dry riverbed across the high plain, a convoy that will not let you pass, and a road with room for one of you. Salem says he has driven worse.',
      parts: ['The riverbed', 'The convoy', 'The narrows', 'The lava fields'],
      boss: 'An armoured bus, with the whole convoy\'s luggage still tied to the roof.' },
    { id: 'sanaa', stage: 7, name: 'Bab al-Yemen', place: 'Sana\'a', road: 'The last mission', built: false, next: ['marib'], bow: [-0.1], hq: [28, -6],
      label: [0, 11, 'c'], land: [0, -12], stamp: [-30, 14],
      brief: 'The old city of Sana\'a, its tower houses trimmed in white like iced cake, and at its gate, Bab al-Yemen, the Zanabeel waiting with everything the Scorpion ever sent them.',
      parts: ['The city wall', 'The tower houses', 'The old market', 'The gate'],
      boss: 'The Scorpion\'s own war machine, shipped across the water in pieces: a scorpion the size of a house, with the sting to match.' },
    { id: 'marib', stage: 0, name: 'The Old Dam', place: 'Marib', road: 'Secret', built: false, secret: true, next: [], bow: [],
      label: [0, 11, 'c'], land: [24, -2], stamp: [28, 12],
      brief: 'The Scorpion always has a plan B, and the Zanabeel always have an Uncle. This one is out east, at the old dam where the sands begin. Nobody has checked whether there is any water in it.',
      parts: ['The sands', 'The dry reservoir', 'The sluice gate', 'The buried hangar'],
      boss: 'The Scorpion himself, come across the water to see what his Zanabeel have been doing with his money, and whatever it is he has been hiding under the sand.' }
  ];
})();
