// This file consists of unit tests for functions in utility.js
QUnit.module( 'group student_data_entry' );
QUnit.test('isInArray', function(assert) {
    assert.deepEqual(isInArray('1', ['1','2','3']), true);
    assert.deepEqual(isInArray('', ['1','2','3']), false);
});
QUnit.test('isNumeric', function(assert) {
    assert.deepEqual(isNumeric('-1.5'), true);
    assert.deepEqual(isNumeric('-1.5a'), false); 
});
QUnit.test('checkInputStudent', function(assert) {
    function numberEntry(observation, valueRange, expected) {
        assert.deepEqual(checkInputStudent(observation, 'Number', valueRange, '')['wrongInput'], !expected);
    }
    function textEntry(observation, valueCandidates, expected) {
        assert.deepEqual(checkInputStudent(observation, 'Text', '', valueCandidates)['wrongInput'], !expected);
    }
    numberEntry('1.5','1.0-10.0',true);
    numberEntry('0.8','1.0-10.0',false);
    textEntry('Critical','Critical,Helpful',true);
    textEntry('Criticall','Critical,Helpful',false);
});

QUnit.module( 'group student_select_lab' );
QUnit.test('decomposeClassId', function(assert) {
    var classId = 'BIOL101_FALL2016';
    assert.deepEqual(decomposeClassId(classId), ['BIOL101','FALL2016']);
});
QUnit.test('generateLabId', function(assert) {
    var labName = 'Cortisol2_Carey_Thursday';
    var classId = 'BIOL101_FALL2016';

    assert.deepEqual(generateLabId(labName, classId), labName+':'+classId);
});

QUnit.module( 'group admin_edit_data' );
QUnit.test('decomposeClassId', function(assert) {
    var experimentId = 'Cortisol2_Carey_Thursday:BIOL101_FALL2016:Cortisol Concentration';
    var studentName = 'amyth';

    assert.deepEqual(generateObservationId(experimentId, studentName), experimentId+':'+studentName);  
});

QUnit.module( 'group admin_modify_lab' );
QUnit.test('decomposeClassId', function(assert) {
    var select = document.getElementById("qunit-fixture").getElementsByClassName("valueType")[0];
    select.getElementsByClassName('selectpicker')[0].value = 'Text';
    ShowFieldByChoice()
    var divText =  select.getElementsByClassName('valueCandidates')[0];
    var divNumber =  select.getElementsByClassName('valueRange')[0];
     
    assert.equal(divText.style.display, 'block');
    assert.equal(divNumber.style.display, 'none');

    select.getElementsByClassName('selectpicker')[0].value = 'Number'
    ShowFieldByChoice()
    assert.equal(divText.style.display, 'none');
    assert.equal(divNumber.style.display, 'block');

});