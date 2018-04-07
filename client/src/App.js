import React, { Component } from "react";
import { Grid } from "semantic-ui-react";

import Header from "./Header";

import "./style.css";

class App extends Component {
  render() {
    return (
      <Grid centered columns={2} id="grid-container">
        <Grid.Column textAlign="center" id="grid-header">
          <Header />
        </Grid.Column>
      </Grid>
    );
  }
}

export default App;
