package main

type Artist struct {
	Name string `json:"name,omitempty"`
	Born int    `json:"born,omitempty"`
	Died int    `json:"died,omitempty"`
}

type Country struct {
	Name string `json:"name,omitempty"`
}

type City struct {
	Name      string `json:"name,omitempty"`
	CountryId int    `json:"country_id,omitempty"`
}

type Place struct {
	Name           string `json:"name,omitempty"`
	FoundationDate int    `json:"foundation_date,omitempty"`
	CityId         int    `json:"city_id,omitempty"`
}

type Category struct {
	Name string `json:"name,omitempty"`
}

type Item struct {
	Name         string `json:"name,omitempty"`
	CreationDate int    `json:"creation_date,omitempty"`
	CategoryId   int    `json:"category_id,omitempty"`
	PlaceId      int    `json:"place_id,omitempty"`
	ArtistId     int    `json:"artist_id,omitempty"`
}

type ArtistCountry struct {
	CountryId int `json:"country_id,omitempty"`
	ArtistId  int `json:"artist_id,omitempty"`
}

func ArbitraryDataToSQL

func main() {

}
