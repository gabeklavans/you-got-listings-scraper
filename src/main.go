package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

type ListingProps struct {
	Refs        []string `json:"refs"`
	Price       int      `json:"price"`
	Beds        float32  `json:"beds"`
	Baths       float32  `json:"baths"`
	Date        string   `json:"date"`
	Notes       string   `json:"notes"`
	IsFavorite  bool     `json:"isFavorite"`
	IsDismissed bool     `json:"isDismissed"`
}

func basicAuth(c *gin.Context) {
	user, password, hasAuth := c.Request.BasicAuth()
	if hasAuth && user == os.Getenv("AUTH_USER") && password == os.Getenv("AUTH_PASS") {
		c.Next()
	} else {
		c.Abort()
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}
}

func getListings(c *gin.Context) {
	data, err := os.ReadFile("../data/listings.json")
	if err != nil {
		log.Print(err)
	}

	listingsJson := make(map[string]ListingProps)
	json.Unmarshal(data, &listingsJson)

	c.IndentedJSON(http.StatusOK, listingsJson)
}

func getSites(c *gin.Context) {
	data, err := os.ReadFile("../data/sites.json")
	if err != nil {
		log.Print(err)
	}

	sitesJson := make(map[string]string)
	json.Unmarshal(data, &sitesJson)

	c.IndentedJSON(http.StatusOK, sitesJson)
}

func ping(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"pong": true})
}

func main() {
	err := godotenv.Load("../.env")
	if err != nil {
		log.Fatalf("Error loading .env: %s", err)
	}

	router := gin.Default()

	router.Use(cors.Default())

	router.GET("/ping", basicAuth, ping)
	router.GET("/listings", getListings)
	router.GET("/sites", getSites)

	router.Run("192.168.88.22:8083")
}
