/*
 * Formats a user's display name from first and last name.
 */
function formatName(user) {
  // return the name
  return `${user.first} ${user.last}`;
}

module.exports = { formatName };
