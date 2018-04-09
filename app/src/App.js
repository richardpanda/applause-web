import React, { Component } from "react";
import { Grid } from "semantic-ui-react";

import Header from "./Header";
import PostGrid from "./PostGrid";
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
    const { topic } = this.state;

    return (
      <Grid id="grid-container">
        <Grid.Row centered id="grid-header">
          <Header />
        </Grid.Row>
        <Grid.Row centered>
          <TopicDropdown handleChange={this.handleDropdownChange.bind(this)} />
        </Grid.Row>
        <PostGrid topic={topic} />
      </Grid>
    );
  }
}

export default App;
