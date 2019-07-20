



let process = [
    { id: '#P-8883-30', beforeProcess: '#P-6810-29', workpiece: '#W-554-9', time: 10, machine: '#M-3836-15' },
    { id: '#P-6810-29', beforeProcess: 'Self', workpiece: '#W-554-9', time: 5, machine: '#M-671-13' }
];

let temp = {
    '#W-554-9': { // 工件编号
      '#P-8883-30': { machine: '#M-3836-15', time: 10, order: 1 }, // 工序编号，order表示第几道工序
      '#P-6810-29': { machine: '#M-671-13', time: 5, order: 0 }
    }
};

let result = [
    { workpiece: '#W-554-9', machine: '#M-3836-15', process: '#P-8883-30', time: 10, order: 1 },
    { workpiece: '#W-554-9', machine: '#M-671-13', process: '#P-6810-29', time: 5, order: 0 }
];


  