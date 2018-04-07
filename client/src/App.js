import React, { Component } from "react";
import { Grid } from "semantic-ui-react";

import Header from "./Header";
import TopicDropdown from "./TopicDropdown";

import "./style.css";

class App extends Component {
  state = {
    topic: ""
  };

  handleDropdownChange(_, { value }) {
    this.setState({ topic: value });
  }

  render() {
    return (
      <Grid centered columns={2} id="grid-container">
        <Grid.Row textAlign="center" id="grid-header">
          <Header />
        </Grid.Row>
        <Grid.Row centered>
          <TopicDropdown handleChange={this.handleDropdownChange.bind(this)} />
        </Grid.Row>
      </Grid>
    );
  }
}

export default App;
