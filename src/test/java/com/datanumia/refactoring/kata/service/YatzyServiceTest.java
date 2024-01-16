package com.datanumia.refactoring.kata.service;


import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.datanumia.refactoring.kata.model.CategoryEnum;

import com.datanumia.refactoring.kata.model.YatzyConstants;

/**
 * @author wejden
 *
 */
public class YatzyServiceTest {
	
	public YatzyService yatzyService = new YatzyServiceImpl();

	 @Test
    public void testChanceScoring() {
        int expected = YatzyConstants.SMALL_STRAIGHT_SCORE.getValue();
        int actual = yatzyService.getScore(CategoryEnum.CHANCE, List.of(2, 3, 4, 5, 1));
        assertEquals(expected, actual);
        assertEquals(16, yatzyService.getScore(CategoryEnum.CHANCE, List.of(3, 3, 4, 5, 1)).intValue());
    }

    @Test public void testYatzyScoring() {
        int expected = YatzyConstants.YATZY_SCORE.getValue();
        
        int actual = yatzyService.getScore(CategoryEnum.YATZY, List.of(4,4,4,4,4));

        assertEquals(expected, actual);
        assertEquals(50, yatzyService.getScore(CategoryEnum.YATZY, List.of(6,6,6,6,6)).intValue());
        assertEquals(0, yatzyService.getScore(CategoryEnum.YATZY, List.of(6,6,6,6,3)).intValue());
        		
         		
    }

    
    
    @Test
	public void testOneScoring() {
		assertEquals(1, yatzyService.getScore(CategoryEnum.ONES, List.of(1, 2, 3, 4, 5)).intValue());
		assertEquals(2, yatzyService.getScore(CategoryEnum.ONES, List.of(1, 2, 1, 4, 5)).intValue());
		assertEquals(0, yatzyService.getScore(CategoryEnum.ONES, List.of(6, 2, 2, 4, 5)).intValue());
		assertEquals(4, yatzyService.getScore(CategoryEnum.ONES, List.of(1, 2, 1, 1, 1)).intValue());

	}


    @Test
    public void testTwoScoring() {
    	assertEquals(4, yatzyService.getScore(CategoryEnum.TWOS, List.of(1, 2, 3, 2, 6)).intValue());
		assertEquals(10, yatzyService.getScore(CategoryEnum.TWOS, List.of(2, 2, 2, 2, 2)).intValue());

    }

    @Test
    public void testThreeScoring() {
    	assertEquals(6, yatzyService.getScore(CategoryEnum.THREES, List.of(1, 2, 3, 2, 3)).intValue());
		assertEquals(12, yatzyService.getScore(CategoryEnum.THREES, List.of(2, 3, 3, 3, 3)).intValue());

    }

    @Test
    public void testFourScoring()
    {
    	assertEquals(12, yatzyService.getScore(CategoryEnum.FOURS, List.of(4, 4, 4, 5, 5)).intValue());
		assertEquals(8, yatzyService.getScore(CategoryEnum.FOURS, List.of(4, 4, 5, 5, 5)).intValue());
		assertEquals(4, yatzyService.getScore(CategoryEnum.FOURS, List.of(4, 5, 5, 5, 5)).intValue());

    }

    @Test
    public void testFiveScoring()
    {
    	assertEquals(10, yatzyService.getScore(CategoryEnum.FIVES, List.of(4, 4, 4, 5, 5)).intValue());
		assertEquals(15, yatzyService.getScore(CategoryEnum.FIVES, List.of(4, 4, 5, 5, 5)).intValue());
		assertEquals(20, yatzyService.getScore(CategoryEnum.FIVES, List.of(4, 5, 5, 5, 5)).intValue());

    }

    @Test
    public void testSixScoring()
    {
    	assertEquals(0, yatzyService.getScore(CategoryEnum.SIXES, List.of(4, 4, 4, 5, 5)).intValue());
		assertEquals(6, yatzyService.getScore(CategoryEnum.SIXES, List.of(4, 4, 6, 5, 5)).intValue());
		assertEquals(18, yatzyService.getScore(CategoryEnum.SIXES, List.of(6, 5, 6, 6, 5)).intValue());
    }

    @Test
    public void testOnePairScoring()
    {
    	assertEquals(6, yatzyService.getScore(CategoryEnum.PAIR, List.of(3, 4, 3, 5, 6)).intValue());
		assertEquals(10, yatzyService.getScore(CategoryEnum.PAIR, List.of(5, 3, 3, 3, 5)).intValue());
		assertEquals(12, yatzyService.getScore(CategoryEnum.PAIR, List.of(5, 3, 6, 6, 5)).intValue());

    }

    @Test
    public void testTwoPairScoring()
    {
    	assertEquals(16, yatzyService.getScore(CategoryEnum.TWO_PAIRS, List.of(3, 3, 5, 4, 5)).intValue());
		assertEquals(16, yatzyService.getScore(CategoryEnum.TWO_PAIRS, List.of(3, 3, 5, 5, 5)).intValue());

    }

    @Test
    public void testThreeOfKindScoring()
    {
    	assertEquals(9, yatzyService.getScore(CategoryEnum.THREE_OF_KIND, List.of(3, 3, 3, 4, 5)).intValue());
		assertEquals(15, yatzyService.getScore(CategoryEnum.THREE_OF_KIND, List.of(5, 3, 5, 4, 5)).intValue());
		assertEquals(9, yatzyService.getScore(CategoryEnum.THREE_OF_KIND, List.of(3, 3, 3, 3, 5)).intValue());
	}

    @Test
    public void testFourOfKindScoring()
    {

        
        assertEquals(12, yatzyService.getScore(CategoryEnum.FOUR_OF_KIND, List.of(3, 3, 3, 3, 5)).intValue());
		assertEquals(20, yatzyService.getScore(CategoryEnum.FOUR_OF_KIND, List.of(5, 5, 5, 4, 5)).intValue());
		assertEquals(12, yatzyService.getScore(CategoryEnum.FOUR_OF_KIND, List.of(3, 3, 3, 3, 3)).intValue());

    }

    @Test
    public void testSmallStraightScoring()
    {
    	assertEquals(15, yatzyService.getScore(CategoryEnum.SMALL_STRAIGHT, List.of(1, 2, 3, 4, 5)).intValue());
		assertEquals(15, yatzyService.getScore(CategoryEnum.SMALL_STRAIGHT, List.of(2, 3, 4, 5, 1)).intValue());
		assertEquals(0, yatzyService.getScore(CategoryEnum.SMALL_STRAIGHT, List.of(1, 2, 2, 4, 5)).intValue());

	}

    @Test
    public void testMargeStraightScoring()
    {assertEquals(20, yatzyService.getScore(CategoryEnum.LARGE_STRAIGHT, List.of(6, 2, 3, 4, 5)).intValue());
	assertEquals(20, yatzyService.getScore(CategoryEnum.LARGE_STRAIGHT, List.of(2, 3, 4, 5, 6)).intValue());
	assertEquals(0, yatzyService.getScore(CategoryEnum.LARGE_STRAIGHT, List.of(1, 2, 2, 4, 5)).intValue());

    }

    @Test
    public void testFullHouseScoring()
    {
    	assertEquals(18, yatzyService.getScore(CategoryEnum.FULL_HOUSE, List.of(6, 2, 2, 2, 6)).intValue());
		assertEquals(0, yatzyService.getScore(CategoryEnum.FULL_HOUSE, List.of(2, 3, 4, 5, 6)).intValue());
    }
}
