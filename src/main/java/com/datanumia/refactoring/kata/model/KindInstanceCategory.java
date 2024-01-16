package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class KindInstanceCategory implements Category {

	private Integer dice;

	public KindInstanceCategory(Integer dice) {
		this.dice = dice;
	}

	@Override
	public int getScore(DiceRoll diceRoll) {
		return diceRoll.getDiceCountsGreaterThan(dice).stream().findAny().orElse(0) * dice;
	}

}
