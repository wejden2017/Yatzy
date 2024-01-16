package com.datanumia.refactoring.kata.game;
import java.util.logging.Logger;
import java.util.List;

import com.datanumia.refactoring.kata.model.CategoryEnum;
import com.datanumia.refactoring.kata.service.YatzyService;
import com.datanumia.refactoring.kata.service.YatzyServiceImpl;


public class GameApplication {
    private static final Logger logger = Logger.getLogger(GameApplication.class.getName());

    public static void main(String[] args) {
        logger.info("*******Welcome to Yatzy!**********");

        YatzyService yatzyService = new YatzyServiceImpl();

        List<Integer> diceRoll = List.of(1,1,3,3,6 );
        CategoryEnum category = CategoryEnum.CHANCE; // Choose a category
        Integer score = yatzyService.getScore(category, diceRoll);
        logger.info("Score for " + category + ": " + score);
 
        int totalScore = playRound(yatzyService);
        logger.info("Total Score: " + totalScore);

        logger.info("*******End Of The Game!**********");
    }

    private static int playRound(YatzyService yatzyService) {
     

        List<Integer> diceRoll = rollDice();

        CategoryEnum category = CategoryEnum.YATZY; // Replace with the chosen category
        Integer roundScore = yatzyService.getScore(category, diceRoll);

        return roundScore != null ? roundScore : 0;
    }

    private static List<Integer> rollDice() {
        return List.of(1,1,1,1,1);
    }}
