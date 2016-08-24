// This file contains several global constant variables
//To avoid backslash character to be evaluated as escape sequences
var PATTERN_FOR_NAME = String.raw`[-a-zA-Z0-9,\s]{1,60}`;
var PATTERN_FOR_NAME_HINT = "must be a combination of some of the following: number(s),"+
                          " letter(s), hyphen(s), comma(s) and white space(s) with length between 1 and 60";
var PATTERN_FOR_EXPERIMENT_DESCRIPTION = ".{,500}";
var PATTERN_FOR_EXPERIMENT_DESCRIPTION_HINT = "no more than 500 characters";
var PATTERN_FOR_VALUE_CANDIDATES = String.raw`[0-9a-zA-Z\-]*(,[0-9a-zA-Z\-]*)*`;
var PATTERN_FOR_VALUE_CANDIDATES_HINT = "valueCandidates should be in the format:N,C";
var PATTERN_FOR_VALUE_RANGE = "[0-9]{1,10}[.]?[0-9]{0,10}-[0-9]{1,10}[.]?[0-9]{0,10}";
var PATTERN_FOR_VALUE_RANGE_HINT = "valueRange should be in the format:0.3-6.5";
