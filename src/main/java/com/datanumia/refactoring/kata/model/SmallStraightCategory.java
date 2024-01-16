package com.datanumia.refactoring.kata.model;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * @author wejden
 *
 */
public class SmallStraightCategory  extends StraightCategory {
	
    public SmallStraightCategory() {
        super( YatzyConstants.SMALL_STRAIGHT_SCORE.getValue());
       
    }

    @Override
    protected boolean isStraight(DiceRoll diceRoll) {
    	   Set<Integer> uniqueValues = new HashSet<>(diceRoll.getDices());
    	    return uniqueValues.size() == 5 && uniqueValues.containsAll(List.of(1, 2, 3, 4, 5));


    }
    
}