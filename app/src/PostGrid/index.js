import React, { Component } from "react";
import { Card, Grid, Responsive } from "semantic-ui-react";

import PostCard from "../PostCard";

import "./style.css";

class PostGrid extends Component {
  state = {
    posts: []
  };

  async componentWillUpdate(nextProps, _) {
    if (this.props.topic !== nextProps.topic) {
      const response = await fetch(`/api/topic/${nextProps.topic}/posts`);
      const payload = await response.json();
      this.setState({ posts: payload.posts });
    }
  }

  render() {
    const postCards = this.state.posts.map(post => (
      <PostCard key={post.url} post={post} />
    ));

    return (
      <Grid id="post-grid">
        <Responsive maxWidth={535}>
          <Card.Group itemsPerRow={1} centered>
            {postCards}
          </Card.Group>
        </Responsive>
        <Responsive minWidth={535} maxWidth={915}>
          <Card.Group itemsPerRow={2} centered>
            {postCards}
          </Card.Group>
        </Responsive>
        <Responsive minWidth={915}>
          <Card.Group itemsPerRow={4} centered>
            {postCards}
          </Card.Group>
        </Responsive>
      </Grid>
    );
  }
}

export default PostGrid;
