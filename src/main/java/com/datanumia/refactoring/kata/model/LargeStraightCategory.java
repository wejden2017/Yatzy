package com.datanumia.refactoring.kata.model;

import java.util.List;
import java.util.stream.Collectors;

/**
 * @author wejden
 *
 */
public class LargeStraightCategory extends StraightCategory {
	
	public LargeStraightCategory() {
		super(YatzyConstants.LARGE_STRAIGHT_SCORE.getValue());
	}

	@Override
	protected boolean isStraight(DiceRoll diceRoll) {

		return diceRoll.getDices().stream().sorted().collect(Collectors.toList()).equals(List.of(2, 3, 4, 5, 6));

	}

}
