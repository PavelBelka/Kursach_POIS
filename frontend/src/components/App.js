import React, { Component } from 'react';
import { render } from "react-dom";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      loaded: false,
      placeholder: "Loading"
    };
  }

  componentDidMount() {
    fetch("api/books")
      .then(response => {
        if (response.status > 400) {
          return this.setState(() => {
            return { placeholder: "Something went wrong!" };
          });
        }
        return response.json();
      })
      .then(data => {
        this.setState(() => {
          return {
            data,
            loaded: true
          };
        });
      });
  }

  render() {
    return (
      <ol>
        {this.state.data.map(book => {
          return (
            <li key={book.id}>
              Название книги: {book.title}
			  <br/>
			  isbn: {book.isbn}
			  <br/>
			  Автор: {book.authors.map(author => {
						return (
						<div>
							{author.first_name} {author.last_name}
						</div>
						);
			  })}
			  <br/>
			  Жанр: {book.genre.map(genres => {
						return(
						<div>
							{genres.name}
						</div>
						);
			  })}
			  <hr style={{align: "left", color: "black", backgroundColor: "black",height: 0, width:400, marginLeft: 0}}/>
            </li>
          );
        })}
      </ol>
    );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);