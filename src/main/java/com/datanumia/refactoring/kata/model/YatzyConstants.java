package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public enum YatzyConstants {

    SMALL_STRAIGHT_SCORE(15),
    LARGE_STRAIGHT_SCORE(20),
    YATZY_SCORE(50);

    private final int value;

    YatzyConstants(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

}